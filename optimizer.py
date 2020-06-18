""" Code for blog post """

import os
import shutil
import subprocess
import ray

import numpy as np
import fitz

from mlflow.tracking import MlflowClient
from hyperopt import hp
from intervaltree import IntervalTree, Interval
from ray import tune
from ray.tune import Trainable
from ray.tune.schedulers import AsyncHyperBandScheduler
from ray.tune.suggest.hyperopt import HyperOptSearch
from ray.tune.logger import MLFLowLogger, DEFAULT_LOGGERS

num_samples_per_axis = 51


def create_temporary_copy(path):
    tmp_path = os.path.join(os.getcwd(), "source")
    #Path(tmp_path).mkdir(parents=True, exist_ok=True)

    try:
        shutil.copytree(path, tmp_path)
        macro_path = os.path.join(os.getcwd(), "macros.tex")
        macro_copy_path = os.path.join(tmp_path, "macros.tex")
        shutil.copyfile(macro_path, macro_copy_path)
    except:
        pass

    return tmp_path


def get_interval_width(interval, points_per_inch=72):
    """
    Helper function to get the width of an intervaltree.Interval
    in inches.
    """
    return (interval.end - interval.begin) / \
        points_per_inch


def get_variable_def(k, v):
    """
    \\defVal{name}{value}
    """

    return fr"\defVal{{{k}}}{{{v}}}"


def write_variables(conf, tp):
    """ Write variables to file """

    with open(os.path.join(tp, "values.tex"), "w") as f:
        for k, v in conf.items():
            if k.startswith("var-"):
                macro = get_variable_def(k.replace("var-", ""), v)
                f.write(f"{macro}\n")


def compile_latex(filename):
    """
    1. Clean using latexmk
    2. Compile the LaTeX code using latexmk
    """

    working_directory, texfile = os.path.split(filename)

    command = ["latexmk", "-C", texfile]

    try:
        p1 = subprocess.Popen(
            command, cwd=working_directory,
            stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            close_fds=True)
        p1.wait(timeout=15)

        command = ["latexmk", "-pdf", texfile]

        p2 = subprocess.Popen(
            command, cwd=working_directory,
            stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            close_fds=True)

        p2.wait(timeout=15)

        # Clean up
        if p1 is not None:
            p1.kill()
        if p2 is not None:
            p2.kill()

        return True

    except subprocess.TimeoutExpired:
        return True


class MyTrainable(Trainable):
    """
    See Ray Tune
    """

    def _setup(self, conf):

        self.filename = conf["filename"]

        self.basepath = conf["base-path"]
        self.temppath = create_temporary_copy(self.basepath)

        self.texfile = os.path.join(self.temppath, self.filename)
        pre, _ = os.path.splitext(self.texfile)
        self.pdffile = pre + ".pdf"

        print(self.pdffile)
        self.config = conf
        self.lmbda = config["lambda"]

    def _train(self):

        write_variables(self.config, self.temppath)
        done = compile_latex(self.texfile)

        if done:
            loss = -1.0 * (self.calculate_cost() + self.lmbda *
                           self.calculate_regularization())
        else:
            loss = None

        return {"score": loss, "done": done}

    def reset_config(self, new_config):
        self.config = new_config
        write_variables(self.config, self.temppath)
        return True

    def _stop(self):
        pass

    def calculate_regularization(self, ord=2):
        return np.linalg.norm([1 - v for k, v in self.config.items() if k.startswith("var-")], ord=2)

    def calculate_cost(self):

        pdf_document = fitz.open(self.pdffile)

        if pdf_document.pageCount > 3:
            return 10000

        page1 = pdf_document[-1]

        full_tree_y = IntervalTree()
        tree_y = IntervalTree()

        blks = page1.getTextBlocks()  # Read text blocks of input page

        # Calculate CropBox & displacement
        disp = fitz.Rect(page1.CropBoxPosition, page1.CropBoxPosition)

        croprect = page1.rect + disp
        full_tree_y.add(Interval(croprect[1], croprect[3]))

        for b in blks:  # loop through the blocks
            r = fitz.Rect(b[:4])  # block rectangle

            # add dislacement of original /CropBox
            r += disp
            _, y0, _, y1 = r

            tree_y.add(Interval(y0, y1))

        tree_y.merge_overlaps()

        for i in tree_y:
            full_tree_y.add(i)

        full_tree_y.split_overlaps()

        # For top and bottom margins, we only know they are the first and
        # last elements in the list
        full_tree_y_list = list(sorted(full_tree_y))
        _, bottom_margin = \
            map(
                get_interval_width,
                full_tree_y_list[::len(full_tree_y_list) - 1]
            )

        return bottom_margin


def grid_search(conf):

    conf.update(
        {
            "var-figonewidth": tune.grid_search(np.linspace(0, 1, num_samples_per_axis).tolist()),
            #"var-figtwowidth": tune.grid_search(np.linspace(0, 1, num_samples_per_axis).tolist()),
        })

    scheduler = AsyncHyperBandScheduler(metric="score", mode="max")

    return tune.run(
        MyTrainable,
        name=config["name"],
        config=conf,
        scheduler=scheduler,
        verbose=1,
        resources_per_trial=config["resources"],
        num_samples=1,
        max_failures=3,
        reuse_actors=True)


def hyper_search(conf):

    experiment_id = MlflowClient().create_experiment(config["name"])

    conf.update({"mlflow_experiment_id": experiment_id})

    space = {
        'var-figonewidth': hp.uniform('var-figonewidth', 0, 1),
        'var-figtwowidth': hp.uniform('var-figtwowidth', 0, 1),
    }

    current_best_params = [
        {'var-figonewidth': .75, 'var-figtwowidth': .75},
        {'var-figonewidth': .65, 'var-figtwowidth': .65}
    ]

    algo = HyperOptSearch(space, metric="score", mode="max",
                          points_to_evaluate=current_best_params,
                          n_initial_points=5)

    scheduler = AsyncHyperBandScheduler(metric="score", mode="max")

    return tune.run(
        MyTrainable, name=config["name"],
        scheduler=scheduler, search_alg=algo,
        config=conf, verbose=1,
        resources_per_trial=config["resources"],
        num_samples=num_samples_per_axis,
        reuse_actors=True,
        loggers=DEFAULT_LOGGERS + (MLFLowLogger, ))


if __name__ == "__main__":

    tune.register_trainable('MyTrainable', MyTrainable)

    basepath = os.getcwd()

    # Save two CPUs for other things ;)
    ray.init(num_cpus=6)

    # for cpus in [1, 2, 4, 6]:
    cpus = 1
    config = {
        "filename": "conference_101719.tex",
        "base-path": os.path.join(basepath, "example", "constraint"),
        "lambda": 0,
        "resources": {"cpu": cpus},
        "name": f"LaTeX-GridSearch-{cpus}"
    }

    #     # ray.init(local_mode=True)

    analysis = grid_search(config)

    df = analysis.dataframe()
    df.to_pickle(f"./dummy_gs_{cpus}.pkl")

    config["lambda"] = 2 * np.pi
    config["name"] = "LaTeX-hyperopt"
    analysis = hyper_search(config)

    best_config = analysis.get_best_config(metric="score")
    print("Best config: ", best_config)

    write_variables(best_config, os.path.join(
        basepath, "example", "constraint"))

    compile_latex(os.path.join(basepath, config["filename"]))

    df = analysis.dataframe()
    print(df)
    df.to_pickle("./dummy.pkl")

import timeit, os
from constraint_gs import MyTrainable
import numpy as np

def loop():
    """
    The training loop
    """

    myt = MyTrainable(config)
    myt._train()


if __name__ == "__main__":

    basepath = os.getcwd()
    config = {
        "filename": "conference_101719.tex",
        "base-path": os.path.join(basepath, "example", "constraint"),
        'var-figonewidth': .5,
        'var-figtwowidth': .5,
    }

    r = timeit.repeat(stmt=loop, repeat=2601, number=1)

    print(r)
    np.save("raw_compile", r)
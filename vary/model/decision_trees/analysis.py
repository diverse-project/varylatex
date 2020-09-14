# Based on this example on DecisionTrees with scikit learn :
# http://chrisstrelioff.ws/sandbox/2015/06/08/decision_trees_in_python_with_scikit_learn_and_pandas.html
# Basic imports
import os
import subprocess

# Data manipulation imports
from sklearn.tree import DecisionTreeClassifier, export_graphviz
import pandas as pd


def visualize_tree(tree, feature_names, output_path):
    """
    Creates a PNG image of a decision tree and exports it in the folder specified bu output_path.
    The name of the image is dt.png.
    """
    dot_path = os.path.join(output_path, "dt.dot")
    img_path = os.path.join(output_path, "dt.png")
    with open(dot_path, 'w') as f:
        export_graphviz(tree, out_file=f,
                        feature_names=feature_names,
                        filled=True,
                        special_characters=True,
                        rounded=True,
                        class_names=list(map(str, tree.classes_)))
    command = ["dot", "-Tpng", dot_path, "-o", img_path]
    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError:
        exit("Could not run dot, ie graphviz, to "
             "produce visualization")


def load_csv(csv_path):
    """
    Creates a dataframe based on the CSV path
    """
    return pd.read_csv(csv_path, index_col=0)


def refine_csv(df):
    """
    Transforms the categorical values (typically strings) of the sets into integers that could
    be exploited by the DecisionTree. It uses the One-hot method.
    """
    # Set of categorical values
    cat_vals = set()

    # Change string (seen as objects) values to booleans
    for col_name, col_type in dict(df.dtypes).items():
        if col_type == 'O':  # If this is a column of objects (true for strings)
            df = pd.concat([df, pd.get_dummies(df[col_name], prefix=col_name)], axis=1)
            cat_vals.add(col_name)

    # Get all the features except the class (nbPages), the remaining space, and initial categorical features
    features = list(set(df.columns) - set(["nbPages", "space"]) - cat_vals)

    return df, features


def get_sample_size(df, perc):
    """
    The size of the training set based on a percentage of the total dataframe
    """
    return int(len(df)*float(perc)/100)


def split_frame(df, features, sample_size, max_pages):
    """
    Separates the dataframe into training and testing set and gives the results for every entry
    """
    y = (df["nbPages"] <= max_pages) & (df["space"] >= 0)
    train = df[features][:sample_size]
    test = df[features][sample_size:]
    return train, test, y


def create_dt(train, y, sample, min_samples_split=10, random_state=99):
    dt = DecisionTreeClassifier(min_samples_split=min_samples_split, random_state=random_state)
    dt.fit(train, y[:sample])
    return dt


def decision_tree(csv_path, max_pages, perc=100, output_path=None):
    """
    Returns the classifier and the array of the feature names
    """
    df = load_csv(csv_path)
    # Replace string values by booleans with one-hot method
    df, features = refine_csv(df)
    sample_size = get_sample_size(df, perc)
    train, test, y = split_frame(df, features, sample_size, max_pages)
    classifier = create_dt(train, y, sample_size, min_samples_split=4)
    
    # Only useful for testing, but we may use 100% of the data for training, and skip the computing of the accuracy
    if perc < 100:
        print("Accuracy :", classifier.score(test, y[sample_size:]))

    # Generate a .dot and a .png file of the tree if there is an output path
    if output_path:
        visualize_tree(classifier, features, output_path)

    return classifier, features


def predict(classifier, config, config_src, features):
    """
    Uses tre decision tree to estimate the probability of a config (which can have incomplete data)
    to match the target class
    """
    internal_tree = classifier.tree_
    # Modify the config to adapt categorical values
    newconfig = config.copy()

    for name in config_src["enums"]:
        val = config.get(name)
        if val:
            del newconfig[name]
            for possible_value in config_src["enums"][name]:
                temp_name = pd.get_dummies(possible_value, prefix=name).columns[0]
                newconfig[temp_name] = 0
            newname = pd.get_dummies(val, prefix=name).columns[0]
            newconfig[newname] = 1
            
    # Go through the nodes and store the population for each class in the accumulator
    def recurse(node_id, acc):
        # End condition : leaf node
        if internal_tree.children_right[node_id] == internal_tree.children_left[node_id]:
            # Add the populations of the leaf to the accumulator
            res = list(map(sum, zip(acc, list(internal_tree.value[node_id][0]))))
            return res
        # The feature used in this node
        ft = features[internal_tree.feature[node_id]]
        value = newconfig.get(ft)
        # If the value is defined then follow the corresponding path, otherwise work on the populations
        # on the two branches
        if value is not None:
            if value == "true":
                value = 1
            if value == "false":
                value = 0
            if float(value) > internal_tree.threshold[node_id]:
                return recurse(internal_tree.children_right[node_id], acc)
            else:
                return recurse(internal_tree.children_left[node_id], acc)
        else:
            new_acc = recurse(internal_tree.children_right[node_id], acc)
            return recurse(internal_tree.children_left[node_id], new_acc)

    pop = recurse(0, [0]*internal_tree.n_classes[0])

    total = sum(pop)
    classes = list(classifier.classes_)
    if True not in classes:
        return 0
    target_index = classes.index(True)
    return pop[target_index] / total


def eval_options(classifier, config, config_src, features):
    """
    For a given config, evaluates the probability for a config one change away to match the target class.
    Returns a dictionary similar to a configuration source but with probabilities.
    Structure :
    {
        "enums" : {
            <e_name1> : {
                "default" : <proba_default>,
                "values" : {
                    <val1_1> : <e_prob1_1>,
                    ...
                    <val1_n> : <e_prob1_n>
                }
            },
            <e_name2> : { ... },
            ...
        },
        "booleans" : {
            <b_name1> : {
                "default" : <b_prob1>
                "false" : <b_prob1_false>,
                "true" : <b_prob1_true>,
            },
            <b_name2> : { ... }
        },
        "choices" : {
            <c_name1> : <c_prob1>,
            <c_name2> : <c_prob2>,
            ...
        },
        "numbers" : {
            <n_name1> : {
                "default" : <n_prob1>,
                "limits" [
                    {"lower" : <lower_1_1>, "upper" : <upper_1_1>, "prob" : <n_prob1_1>},
                    {"lower" : <lower_1_2>, "upper" : <upper_1_2>, "prob" : <n_prob1_2>},
                    { ... },
                    ...
                ]
            }
        }
    }
    """
    prob_dict = {}
    temp_cfg = config.copy()

    # enums
    enums = {}
    for name, values in config_src["enums"].items():
        enums[name] = {}
        probas = {}

        for val in values:
            temp_cfg[name] = val
            probas[val] = predict(classifier, temp_cfg, config_src, features)
        
        del temp_cfg[name]
        enums[name]["default"] = predict(classifier, temp_cfg, config_src, features)

        if name in config:
            temp_cfg[name] = config[name]
        enums[name]["values"] = probas

    prob_dict["enums"] = enums
 
    # booleans
    booleans = {}
    for name in config_src["booleans"]:
        probas = {}
        for val in [True, False]:
            temp_cfg[name] = val
            probas[val] = predict(classifier, temp_cfg, config_src, features)
        
        del temp_cfg[name]
        probas["default"] = predict(classifier, temp_cfg, config_src, features)

        if name in config:
            temp_cfg[name] = config[name]
        booleans[name] = probas

    prob_dict["booleans"] = booleans
    
    # choices
    choices = {}
    for group in config_src["choices"]:
        selected_value = None
        for name in group:
            if name in temp_cfg:
                del temp_cfg[name]
            if name in config:
                selected_value = name
        for name in group:
            temp_cfg[name] = True
            choices[name] = predict(classifier, temp_cfg, config_src, features)
            del temp_cfg[name]
        if selected_value:
            temp_cfg[selected_value] = config[selected_value]

    prob_dict["choices"] = choices

    # numbers
    numbers = {}

    for name, domain in config_src["numbers"].items():
        numbers[name] = {}
        min_bound, max_bound, _ = domain
        numbers[name]["limits"] = []
        internal_tree = classifier.tree_
        thresholds = \
            [min_bound] + \
            [internal_tree.threshold[i] for i, n in enumerate(internal_tree.feature) if n >= 0 and features[n] == name] + \
            [max_bound]
        thresholds.sort()
        
        for lower, upper in (zip(thresholds[:-1], thresholds[1:])):
            average = (lower + upper) / 2
            temp_cfg[name] = average
            numbers[name]["limits"].append({
                "lower": lower,
                "upper": upper,
                "prob": predict(classifier, temp_cfg, config_src, features)
            })
            del temp_cfg[name]
            numbers[name]["default"] = predict(classifier, temp_cfg, config_src, features)

            if name in config:
                temp_cfg[name] = config[name]
    prob_dict["numbers"] = numbers

    return prob_dict


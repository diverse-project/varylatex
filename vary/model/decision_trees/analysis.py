# Based on this example on DecisionTrees with scikit learn :
# http://chrisstrelioff.ws/sandbox/2015/06/08/decision_trees_in_python_with_scikit_learn_and_pandas.html
# Basic imports
import os
import subprocess

# Data manipulation imports
from sklearn.tree import DecisionTreeClassifier, export_graphviz
import pandas as pd


def visualize_tree(tree, feature_names, output_path):
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
    return pd.read_csv(csv_path, index_col = 0)


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


def split_frame(df, features, sample_size):
    """
    Separates the dataframe into training and testing set and gives the results for every entry
    """
    y = df["nbPages"]
    train = df[features][:sample_size]
    test = df[features][sample_size:]
    return train, test, y


def create_dt(train, y, sample, min_samples_split=10, random_state=99):
    dt = DecisionTreeClassifier(min_samples_split=min_samples_split, random_state=random_state)
    dt.fit(train, y[:sample])
    return dt


def decision_tree(csv_path, perc=100, output_path=None):
    df = load_csv(csv_path)
    # Replace string values by booleans with one-hot method
    df, features = refine_csv(df)
    sample_size = get_sample_size(df, perc)
    train, test, y = split_frame(df, features, sample_size)
    classifier = create_dt(train, y, sample_size, min_samples_split=4)
    
    # Only useful for testing, but we may use 100% of the data for training, and skip the computing of the accuracy
    if perc < 100:
        print("Accuracy :", classifier.score(test, y[sample_size:]))

    # Generate a .dot and a .png file of the tree if there is an output path
    if output_path:
        visualize_tree(classifier, features, output_path)

    return classifier


def predict(classifier, config, features, target_class):
    """
    Uses tre decision tree to estimate the probability of a config (which can have incomplete data)
    to match the target class
    """
    internal_tree = classifier.tree_

    def recurse(node_id, acc):
        if internal_tree.children_right[node_id] == internal_tree.children_left[node_id]:
            res = list(map(sum, zip(acc, list(internal_tree.value[node_id][0]))))
            return res
        ft = features[internal_tree.feature[node_id]]
        print(ft)
        value = config.get(ft)
        print(value)
        if value is not None:
            if value > internal_tree.threshold[node_id]:
                return recurse(internal_tree.children_right[node_id], acc)
            else:
                return recurse(internal_tree.children_left[node_id], acc)
        else:
            new_acc = recurse(internal_tree.children_right[node_id], acc)
            return recurse(internal_tree.children_left[node_id], new_acc)

    pop = recurse(0, [0]*internal_tree.n_classes[0])

    total = sum(pop)
    target_index = list(classifier.classes_).index(target_class)
    return pop[target_index] / total


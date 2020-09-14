# Motivation
With this implementation of VaryLaTeX we want to give the user a way to add variability to a LaTeX document, to help them either  customize a document, or tweak it to match some requirements. For instance, one may want a document that fits on a maximum of 10 pages.

# Adding variability

## Choice between a templating framework and native LaTeX

[The first version of VaryLaTeX](https://github.com/FAMILIAR-project/varylatex) used a templating framework to inject variability into the document. The upside of doing this is that it is not limited to LaTeX documents and can be used for other formats without much teawking.

The downsides of it is that the user has to learn the template syntax and, most importantly, the annotated document would no longer compile whereas a native LaTex solution can make functionnal documents outside of the tool.

Still being able to render the document while writing it being judged as important, we chose to go with the native solution instead of the template one.

## Values and conditionals
There are two ways we want to express variability in our LaTeX documents :
- **Values**, which may be numbers (size of an image, of the margin...) or a choice between values (like different display styles, colors).
- **Booleans**, that can be used to make togglable parts of a document based on whether a variable is true or false.


## Values

In the original implementation of [latex-optimizer](https://gitlab.com/martisak/latex-optimizer/), variables are defined using a file (`macros.tex`) where for each value there is a line like this :
```tex
\def\varname{value}
```
Here, to prevent conflicts with already defined values and offer more naming options, we hide the variables behind the prefix `vary@`.
The syntax for defining a value is :
```tex
\defVal{name}{value}
```
Which behind the scenes creates a command (because `\newcommand` seems recommended over `\def`) like this
```tex
\vary@name
```
The created command expands to `value`

As writing the prefix every time can be tedious and the `@` prevents direct access to the variable, the value can be retrieved using
```tex
\getVal{name}
```

## Conditionals

The other aspect of variability that we need is the ability to toggle parts of the document, using `if` statements and booleans.
The condition that is used here is whether a variable exists or not. A value of `true` will be declared like this :
```tex
\defVal{name}{}
```
A value of `false` will not be defined.

To check if a variable is defined, we use the `\ifcsname` macro that displays its content only if a command with a certain name is defined. As this is an `if` command that is defined in LaTeX, the content ends on `\fi` and it is possible to add an `else` block with `\else`.
The first idea was just to provide an alias of `ifcsname` that would take the name of the variable as a parameter and put it inside `\ifcsname`. This would have allowed the user to use the condition like a normal one, with `\else` and `\fi

The issue with this solution concerns nested `if` conditions like this :
```tex
\ifVal{bool1}
    \ifVal{bool2}
    \fi
\fi
```
In this case, if `bool1` is not defined, the content of the first condition will not be expanded. The block will end at the first `fi` met, which is the one directly after `\ifVal{bool2}`. That means that the part after that `fi` will be executed and an error will be thrown because of the extra `\fi` at the end.

To solve this problem, we use a syntax that is more similar to programming languages, with the conditional block delimited by brackets :
```tex
% Syntax without else block
\ifVal{val}{
    This will only be displayed if val has been defined.
}
% Syntax with else block
\ifValElse{val}{
    This will only be displayed if val has been defined.
}{
    This will only be displsyed if val has not been defined.
}

```

## Summary / How to use the syntax :
To declare a value :
```tex
\defVal{name}{value}
% Example :
\defVal{img_ratio}{0.75}
```
To declare a boolean set to true :
```tex
\defVal{name}{}
```
To get the value of a defined variable :
```tex
% If the value has not been defined, this will throw an error
\getVal{name}
```
Conditionals :
```tex
\defVal{defined}{}

\ifVal{defined}{This is displayed}
\ifVal{not_defined}{This is not}

\ifValElse{defined}{This is displayed}{And this is not}
```

## Representing the domain of definition of the variables

If we want to generate possible values for our variavles, we need to specify their name and definition domain. To do this, we add a file to the project, called ``variables.json. It can define 4 types of variables :
- `booleans` : either defined or not.
- `enums` : defined to one of the possible values
- `choices` : groups of booleans where only one is defined
- `numbers` : floating point numbers, with min, max and decimal precision.
The structure of the file is as follows (order is not important) :
```json
{
    "booleans": ["bool_name_1", ..., "bool_name_n"],
    "enums": {
        "enum_name_1" : ["enum_1_a", ..., "enum_1_z"],
        "enum_name_2" : ...
    }
    "choices": [
        ["choice_1_a", ..., "choice_1_z"],
        ...
        ["choice_n_a", ...]
    ],
    "numbers": {
        "num_name_1": [min, max, precision],
        ...
        "num_name_n": [min, max, precision]
    }
}
```
An example can be seen [there](../vary/example/fse/variables.json).

The JSON file is then used by the proram to either generate random configurations or to show the possible choices to the user.


# The application

## Timeline
The application started from a `python` script, which itself was inspired by the [latex-optimizer project by Martin Isaksson](https://gitlab.com/martisak/latex-optimizer/).
The first goal was to generate documents with random configurations based on the `variables.json` file.

Then, with those documents, we observe the page counts and how they changed based on the variables. These records are stored in a CSV file that is then used by `scikit-learn` to create a **decision tree** that guesses if a document following a given configuration is going to match the requirements.

All of this was done with a command-line tool but as the number of options was increasing and as it was not very user-friendly, so we decided to create a web-app based on the same concept, which would make the use of the tool easier.

With the app, we finally decided to propose 2 options, one that generates documents to create an estimator and guide the user while setting the variables, and the other that is just here to provide a configurator for the document without trying to check its page count.

We also added a way to generate automatically new variables, for the size when using `\includegraphics` and for the space between elements in a list. These variables can be automatically added to a document without the need for the user to write anything.

## Command-line app
The first idea of the project was to create a tool that we could call from the terminal and that would generate random configurations of a document and then output a CSV file of the results and an image of the decision tree corresponding to the results.

We realized that it was not user-friendly as we needed to specify may options every time, so we decided to create a web application so the user could gain more control through a web interface.

## Server side
As the project was initially written in `python`, we chose a to use `python` framework for making our webapp. We decided to use `Flask` for that.

The functionalities that were used in the command-line app were turned into functions and extracted to common source files, used by both the command-line and the server app.

There are two ways to select a project in the app : the first one is to place everything in a `.zip` file and upload it to the server with the import button. The second one is to have the project on [Overleaf](http://overleaf.com), create a **read-only** link to it and copy and paste the key that links to the project (the key is the part after `https://www.overleaf.com/read/` in the link). The program then gets access to the project and is able to download the `.zip` of the project directly.

## Client side
The client side is a basic interface with HTML, CSS and JavaScript, and bootstrap to simplify the layout.

# Automatically generated variables
Apart from using previously-defined variation points, we wanted to be able to add new variables to a document, and thus have a way to tweak a document that was not intended for VaryLaTeX.

For now, there are two types of variables that can be infered this way. The first one is a variable for each element included via `\includegraphics` : instead of using the specified `height`, `width` or `scale`, we generate a variable whose domain is centered on the original value.
The second one is a variable that changes the space between 2 items in a list, to reduce its size.

The user can choose whether they want to use the variables or to stick with the original document.


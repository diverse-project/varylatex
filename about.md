# Motivation
With this implementation of VaryLaTeX we want to know if this is possible to express the variability of a document without needing a preprocessor or templating engine.
To do this, we need to find if there is a way to define our variables directly in LaTeX.

# Values and conditionals
There are two ways we want to express variability in our LaTeX documents :
- **Values**, which may be numbers (size of an image, of the margin...) or a choice between values (like different display styles, colors).
- **Booleans**, that can be used to make togglable parts of a document based on whether a variable is true or false.


# Values

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

# Conditionals

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

# Summary / How to use the syntax :
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
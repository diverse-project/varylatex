# Add Variability elements in a LaTeX document

## Definitions

Variability can be added to your LaTeX document by two manners :
- Togglable blocks, based on a boolean condition
- Values, that can be either number or strings (that can contain LaTeX macros).

## Apply Variability

To use the variables, you may want to add those two lines in your source document :
```tex
\include{macros}
\include{values}
```
If you don't, the app will do it for you but your document won't be able to compile with another tool (overleaf, `latexmk`...).

You can get the value of a variable with
```tex
\getVal{valName} % Expands to the value
```
Conditionals blocks can be created with `if` and `if-else` commands, the content of the `if` is displayed only if the value with the corresponding name is defined.

```tex
\ifVal{valName} {
    % This part is rendered only if the
    % value is defined
}

\ifValElse{valName} {
    % This part is rendered only if the
    % value is defined
}{
    % This part is rendered only if the
    % value is not defined
}
```

## Defining variables' domain

For the program to generate variations of the document, you need to specify the domain of the variables. It is done by adding a file called `variables.json` in the source folder.

In this file you can declare four types of variable domains :
- `"booleans"` : An array of variables names that can correspond to either `true` or `false`, to be used with `\ifVal` only.
- `"numbers"` : A JSON object mapping the name of the variable with an array of length 3, containing the minimum, the maximum, and the precision of the value.
- `"enums"` : A JSON object mapping the name of a variable with an array of all the possible values it can take.
- `"choices"` : An array of arrays (groups) of booleans, where exactly one boolean is set to `true` for each group.
An example of a `variables.json` file can be found [there](../vary/example/fse/variables.json)


## Manually setting variables

If you want to still be able to work with a preview of your document, you need to add the [macros.tex](../vary/model/macros.tex) file in the source folder, and add definitions of the variables' values in a file called `values.tex`, in the same folder.
To define the variables you need to use the provided `defVal` command :
```tex
\defVal{valName}{} % Used for booleans set to true
\defVal{valName}{value} % For variables that store a value
```
Note : to represent a boolean set to false, you just need to not define it.
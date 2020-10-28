# VaryLaTeX

How to submit a research paper, a technical report, a grant proposal , or a curriculum vitae that respect imposed constraints such as formatting instructions and page limits? It is a [challenging](https://twitter.com/mark_riedl/status/1219800144188772354) [task](https://twitter.com/zacharylipton/status/1282700969386684422), especially when coping with time pressure, isn't it? 
**With VaryLaTeX, simply drop your archive into your Web browser... VaryLaTeX makes automatically vary your PDF to fit the pages limit... and if you're unhappy, you can control different aspects of your document with a configurator** 

![Alt Text](http://phdcomics.com/comics/archive/phd090617s.gif)
http://phdcomics.com/comics.php?f=1971

VaryLaTeX allows users annotating LaTeX source files with variability information, e.g., (de)activating portions of text, tuning figures' sizes, or tweaking line spacing. Then, a fully automated procedure learns constraints among Boolean and numerical values for avoiding non-acceptable paper variants, and finally, users can further configure their papers (e.g., aesthetic considerations) or pick a (random) paper variant that meets constraints, e.g., page limits. 

It's a complete rewrite/extension of https://github.com/FAMILIAR-project/varylatex 
*Feel free to contribute, suggest features, provide feedbacks, use cases* 

There is a short demonstration: https://www.youtube.com/watch?v=u1ralqbHCyM&list=PLcDsXHkK7hJ3n9v7VAMbZCIV6egreI8OL and some technical explanations in this Youtube playlist

## How to run VaryLaTeX?

To initiate the work, we build upon the implementation described on this blog post [LaTeX writing as a constrained non-convex optimization problem](https://blog.martisak.se/2020/06/06/latex-optimizer/) and available on gitlab: https://gitlab.com/martisak/latex-optimizer/ 
(note: "fork" of gitlab as described here: http://ruby.zigzo.com/2015/03/23/moving-from-gitlab-to-github/) 

To run it, you need have `texlive` and `python` (3) installed, then
```
pip install -r requirements.txt
python main_server.py
```
If it does not work, you may want to use `python3` and `pip3` instead of `python` and `pip`.

The app can then be accessed in a browser at [0.0.0.0:5000](http://0.0.0.0:5000/).

You can also run the app within a `Docker` container : to do this, install docker then, in the project folder
```bash
# Create the image
sudo docker build -t varylatex .
# Create the container
sudo docker run -it --rm -p 5000:5000 varylatex
```
And inside the container you can run
```bash
python main_server.py
```

To learn about the implementation and the choices that were made for the project, see [about.md](docs/about.md).

## Publications

More details can be found in the following paper, published/presented at 12th International Workshop on Variability Modelling of Software-Intensive Systems https://vamos2018.wordpress.com/:
"VaryLaTeX: Learning Paper Variants That Meet Constraints" by Mathieu Acher, Paul Temple, Jean-Marc Jézéquel, José A. Galindo, Jabier Martinez, Tewfik Ziadi: https://hal.inria.fr/hal-01659161/

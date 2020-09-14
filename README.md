# VaryLaTeX

It's a complete rewrite/extension of https://github.com/FAMILIAR-project/varylatex

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
sudo docker run -it --rm --name -p 5000:5000 varylatex
```
And inside the container you can run
```bash
python main_server.py
```

To learn about the implementation and the choices that were made for the project, see [about.md](docs/about.md).

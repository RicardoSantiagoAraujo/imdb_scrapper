### Generating documentation:

1- Move into the docs/ directory.

2- Automatically generate .srt files from docstrings in python files modules:

```
sphinx-apidoc -o source/  ../
```

3- Generate the html build (alternatively, epub or others):

```
make html
```

```
make epub
```

It might be a good idea to delete the existing build in docs/build/html before generating the new one.

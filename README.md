# ocus_helper

[source code](https://github.com/megan-fillion/ocus_helper)

you can find the attributed methods in ocus_helper/models

## Download

pip install --upgrade ocus_helper

<pre><code>from ocus_helper.models import Database, Nas, S3</code></pre>

## Add to package

### install packages:
- setuptools
- wheel
- tqdm
- twine

### add code to models.py or add new sibling file

alter line 8 in setup.py
<pre><code>version="0.0.n+1"</code></pre>

### create .pyrirc file

<pre><code>[distutils] 
index-servers=pypi

[pypi]
repository: https://upload.pypi.org/legacy/ 
username: <your username>
password: <your password>

[testpypi]
repository: https://test.pypi.org/legacy/
username: <your username>
password: <your password>
</code></pre>

### push to github

### push to pypi

<pre><code>python3 setup.py sdist bdist_wheel
python -m twine upload dist/*
</code></pre>
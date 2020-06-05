# ocus_helper

[source code](https://github.com/megan-fillion/ocus_helper)
you can find the attributed methods in ocus_helper/models

# To run

pip install --upgrade ocus_helper

<pre><code>from ocus_helper.models import Database, Nas, S3</code></pre>

# To add to package:

1. install packages:
- setuptools
- wheel
- tqdm
- twine

2. add code to models.py or add new sibling file

alter line 8 in setup.py
<pre><code>version="0.0.n+1"</code></pre>

3. create .pyrirc file

<pre><code>
[distutils] 
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

4. push to github

5. push to pypi

<pre><code>
python3 setup.py sdist bdist_wheel
python -m twine upload dist/*
</code></pre>
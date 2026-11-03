# ebrains-drive

**This package has been renamed to [`ebrains-storage`](https://pypi.org/project/ebrains-storage/).**

The name changed in 0.9.0, because the package has long served both EBRAINS Collaboratory storage services — the Drive (Seafile) and the Bucket (Data-Proxy) — so "drive" described only half of it.

What is published here from 0.9.0 onwards is a compatibility stub. It contains almost no code of its own: it requires `ebrains-storage` and re-exports it, so that `pip install ebrains-drive` and `import ebrains_drive` both keep working. Importing `ebrains_drive` emits a `FutureWarning`.

Please install and import the new name:

```bash
pip install ebrains-storage
```

```python
import ebrains_storage

client = ebrains_storage.connect(token="...")
bucket_client = ebrains_storage.connect(token="...", target="bucket")
```

The classes are the same objects under either name, so a code base can be migrated a module at a time.

Documentation, source and issues: <https://github.com/HumanBrainProject/ebrains-storage>

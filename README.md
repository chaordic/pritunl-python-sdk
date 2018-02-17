Pritunl Python SDK
=========

Unofficial [Pritunl](https://pritunl.com) SDK written in Python that allows to easily intract with Pritunl API.

## Install

From dev upstream

```
pip install -e git+git@github.com:chaordic/pritunl-python-sdk.git@master#egg=pritunlsdk
```

From PyPi

```
pip install pritunlapiclient
```

## Dependencies

* Self hosted pritunl
* Valid administrator user
* Valid **token authentication**

Export the following variables in environment:

```shell
export PRITUNL_API_TOKEN=<API_TOKEN>
export PRITUNL_API_SECRET=<API_SECRET>
export PRITUNL_API_URL=<PRITUNL_URL>
```

## Usage

```python
from pritunlsdk import pritunl

pritunl.post_pritunl_user("organization","username",user_groups=['devops','developer'])
```

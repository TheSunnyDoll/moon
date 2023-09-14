# moon

### Proxy
If you need to use a proxy to access the Exchange API, you can set the environment variables as shown in the following example:
```bash
$ export https_proxy=http://127.0.0.1:7890  # these proxies won't work for you, they are here for example
$ export http_proxy=http://127.0.0.1:7890

## talib
conda install -c conda-forge ta-lib -y

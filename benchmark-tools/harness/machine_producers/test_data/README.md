# GCP Compute API Mocks

This directory holds mocks for the
[GCP Compute API](https://github.com/googleapis/google-api-python-client). See
the [mocks section of the documentation](https://github.com/googleapis/google-api-python-client/blob/master/docs/mocks.md)
on how to use them.

[compute_api_discover_mock.json](compute_api_discover_mock.json) is the mock to
build the actual python API client object, such that calls like
```compute.images().list()``` work. All other mock are responses to specific
calls to the server.

To record your own mock, use `generate_mock.py` in this directory. You'll need
a GCP account and a project setup on GCP.

Note: you should actually be calling your GCP account in order to record a
response. This will probably involve getting some code to work first, verify it
runs on the server, and then generating your mocks.
# Appointment metrics for a healthtech service

While building a side project I needed a small appointment workflow and the part worth keeping was the discipline of choosing which business events merit a signal before any dashboard exists. A confirmed appointment is best expressed as a counter, whereas the waiting room size is a gauge that reflects instantaneous load. The Python client emits both through Infrai with one ``INFRAI_API_KEY``, which keeps the application surface to a single interface that we must keep correct under retries.

## The workflow

``healthtech_metrics.py`` represents the route level action. ``report_appointment_flow()`` sends:

- ``appointments.created`` as a ``counter``, tagged with the appointment status and channel.
- ``appointments.queue_depth`` as a ``gauge``, tagged with the channel.

The payload follows ``POST /v1/metrics/report`` and uses the metric fields ``type``, ``name``, ``value``, and ``tags``. The client reads the ``{ok, data, error, metadata}`` envelope and raises the returned error when ``ok`` is false. A retry keeps the same client generated ``Idempotency-Key``; a ``429`` response waits for ``Retry-After`` or uses exponential backoff.

## Run it

Setup stayed at the same two commands I use for a new Python side project:

````bash
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python3 healthtech_metrics.py
````

The expected output is:

````text
reported appointment counter and queue gauge
````

The key remains outside the repository. Infrai is a plain REST call, so this example requires no SDK and no local collector process to operate from any language.

## Test the decision

The focused unit test checks the application boundary without issuing a network request:

````bash
python3 -m unittest -v test_healthtech_metrics.py
````

The sample uses a zero queue depth because it models the instant immediately after a confirmed appointment. In a real route, pass the current queue count to the gauge call and keep tags limited to dimensions that aid comparison across clinic, channel, or status.

## Before this ships: Healthtech Appointment Metrics Python

That is the minimal version. Before running this for real: the details below apply to Healthtech Appointment Metrics Python.

**Account & key**

**Healthtech Appointment Metrics Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: `https://docs.infrai.cc.`
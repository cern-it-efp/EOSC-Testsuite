4. Verification
---------------------------------------------
Run using *--via-backend* so that the proxy at CERN runs the TS (only deploys tests, no provisioning), harvests results and push them to CERN's S3 bucket.
Before starting the run, a message will be shown asking for yes/no answer. It warns the user that backend runs publish results to the CERN bucket.
**Note that this feature is still under development and testing and will be available on next releases.**

# Twitter Streaming 

This folder will contain stuff related to streaming tweets from Twitter.

### Folders:
* `v1-framework` : This folder contains a simple tweet streaming framework written to utilize Twitters V1 API endpoints. This framework writes new-line delimited .json files (each line is one tweet) for each day tweets are streamed. It also includes multiple safety nets which attempt to ensure the stream constantly gathers data in real-time. If the stream unexpectedly breaks, it should automatically reconnect. Furthermore, this frameworks sends automated emails when the streaming script breaks so that you can manually check whether things are working properly. 
* `wip` : This folder includes **W**ork **I**n **P**rogress scripts that are not quite production ready.
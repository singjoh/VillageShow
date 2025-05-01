## Village Show Application

A friendly tracking system for my local village show, please feel free to adapt for other use, though remember to thank the author.
John Singleton
john_singleton01@yahoo.co.uk

## Installation

Please see the details in docs/Village Show Guide.docx regarding deployment of this app to your own kubernetes cluster (a guide on using Docker Desktop kubernetes is included).

Essentially, the deployment phase details:
* Setting up your own local cluster, including required file mounts.
* Building the container from the code using the Dockerfile.
* Deploying the software with the required dependencies (postgres).
  
First time use will need some start-up data, more details in the guide, but essentially:
* Open up the app in a browser, using the localhost (following the guide, this will http://vshow.local)
* Add cup data (without that data then classes cannot be linked to cups).
* Import the class data CSV file, the list of categories for this year, and the cups they relate to.
* Enter the entrant data before the show, and export the pre-show data to set-up before the day.
* After judging, enter the judges data, then export the post-show data.

Have a good time!

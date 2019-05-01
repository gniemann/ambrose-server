# Ambrose-Server

This is the backend for [Ambrose](), a IoT device for building physical project status boards. 

The project is structured into multiple packages:

- ambrose contains the Flask app. It is further split into several packages:

    - api: contains the REST API
    - models: contains the database models as well as the db object
    - services: contains service objects. These are where most of the application logic live, and serve as an intermediaty between the web routes and the models. Services are further split into packages when it makes sense to do so.
    - tasks: poorly names, it contains the celery tasks
    - web: contains all the web routes. It is broken into sub packages. All the packages in this package follow the general convention of a `Blueprint` defined in the `__init__.py` file, with routes defined on it. Each package maintains its own `templates` directory and contains a `forms.py` file with `WTForms` for the package. 
    
- application_insights: contains a service for getting data from Azure Application Insights. 
- devops: contains a service for getting data from Azure DevOps
- json_object: helper object for dealing with JSON
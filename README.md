# database_dashboard

This project implements a custom Python CRUD module for linking a Mongo database to a web-based dashboard.
The dashboard serves a ficticious animal shelter with preset queries, making it easy to identify which of their
animals are best suited for certain search and rescue jobs. Animal geo-positions are located via a map and breed
information is stored in a pie chart at the bottom of the dashboard.

Sometimes the best way to keep an application maintainable, readable, and adaptable, is to compartmentalize components
through encapsulation and abstraction. The CRUD module is separated from the dashboard application, and the CRUD module
takes functionality built with the pyMongo Python module and adapts it for use with this specific database. It would be 
possible to perform all of these duties within the dashboard, but functions and methods would quickly become cluttered,
resulting in a codebase that can be unruly and difficult to perform future adaptations or upgrades to.

As a professional in the computer science realm, it is important to dissect projects into bite-sized chunks with respect
to each component. Organizing each component into charts or visual diagrams can help to excecute the project with minimal
technical debt and depending on whether working independently or in a team, how to tackle each component or how to assign
components to team members.

With some training and practice, anyone can write code. Not everyone can think like a computer scientist or communicate
well with a team, stakeholders, and/or integrate other people's code into their own project. Thinking strategically and 
communicating needs effectively with stakeholders and other developers is critical to go from a coder to an engineer.

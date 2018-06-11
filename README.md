# dpia-tool
The dpia-tool was developed as a support for the implementation of the **Data Protection Impact Assessment (DPIA)**, 
a process required to ensure compliance with the **European General Data Protection Regulation (GDPR)**. 
The tool provides a structured, risk-oriented approach to identification and assessment of potential data protection risks. 
To some extent, the tool is based on the [DPIA template for Smart Grid and smart metering systems](https://ec.europa.eu/energy/sites/ener/files/documents/2014_dpia_smart_grids_forces.pdf), 
however it is not limited to use only in smart grid context. 
The tool can be applied to assessments in other domains.

## Features
- Team work - Direct support for distributed team working
- Guidance - Guidance about how to implement each step embedded directly in the tool
- Hints - Hints about the nature of the required input (tooltips, catalogues)
- Version control - Recover deleted assessments or restore to any previous state
- Reporting - Automatic generation of documentation

## Built with
- Python 2.7
- [Django <= 1.11](https://www.djangoproject.com) - Web framework
- [django-reversion 2.0.12](https://github.com/etianen/django-reversion) - Version control for model instances
- [django-crispy-forms 1.7.0](https://github.com/django-crispy-forms/django-crispy-forms) - Form layouts
- [django-downloadview 1.9](https://github.com/benoitbryon/django-downloadview) - File manager
- [django-widget-tweaks 1.4.1](https://github.com/jazzband/django-widget-tweaks) - Template field customizer
- [python-docx 0.8.6](http://python-docx.readthedocs.io/en/latest/index.html) - Docx generator
- [reportlab 3.4.0](https://docs.djangoproject.com/en/2.0/howto/outputting-pdf/) - PDF generator

## Running the project locally

Install python 2.7.

Download or clone the repository to your local machine:

`git clone https://github.com/CSR-AIT/dpia-tool.git`

Open the main directory and install the requirements:

`pip install -r requirements.txt`

Create and migrate the database (the migration will also populate the database):

`python manage.py makemigrations`

`python manage.py migrate`

Finally, run the development server:

`python manage.py runserver`

The project will be available at 127.0.0.1:8000.

## License
The source code is released under the [MIT License](LICENSE).

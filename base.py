#!py
#coding=utf-8
import os
import sys

from django.conf import settings


# SETTINGS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)
#DEBUG = os.environ.get('DEBUG', 'on') == 'on'
DEBUG = True

SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))

#ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')
ALLOWED_HOSTS = ['127.0.0.1', 'xiaowanzi.tk', 'www.xiaowanzi.tk']

settings.configure(
    DEBUG=DEBUG,
    SECRET_KEY=SECRET_KEY,
    ALLOWED_HOSTS=ALLOWED_HOSTS,
    ROOT_URLCONF=__name__,
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ),
        TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.dirname(__file__),
        ],
        },
        ],
)


# VC
import re
import glob
import jinja2
import markdown
from collections import OrderedDict
from django.conf.urls import url
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse

# from django.views.generic.base import TemplateView
# from django.views.generic import ListView
# VIEWS
# class index(ListView):
#       template_name = 'base.html'
#       paginate_by = 5
#       queryset = range(50)
# 
#       #def get_context_data(self, **kwargs):
#       #       context = super(index, self).get_context_data(**kwargs)
#       #       context['content'] = range(50)
#       #       return context

class webhook(object):
    DOCS_DIR = os.path.join(BASE_DIR, 'docs')
    HTML_DIR = os.path.join(BASE_DIR, 'html')
    JINJA2_DIR = os.path.join(BASE_DIR, 'jinja2')
    IMAGES_DIR = os.path.join(BASE_DIR, 'static/images')

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(JINJA2_DIR))

    # git pull
    cmd = ''' git pull &> /dev/null'''
    os.system(cmd)

    # glob get all markdown files
    MD_FILES = glob.glob(DOCS_DIR+"/*.md")

    # copy docs/{jpeg, jpg, png} into images/ 
    cmd = ''' rsync -avP {src}/*.{jpeg,jpg,png} {dst}/ &> /dev/null '''.format(src=DOCS_DIR, dst=IMAGES_DIR)
    os.system(cmd)

    # parse jinja2 to html
    for_index = OrderedDict()
    template = env.get_template('page.html.jinja2'))
    for MD_FILE in MD_FILES:
        with open(MD_FILE) as f:
            md_content = markdown.markdown(f.read())
        date = "/".join([MD_FILE[:4], MD_FILE[4:6], MD_FILE[6:8]])
        slug = MD_FILE.split('_')[1]
        chinese = MD_FILE.split('_')[-1].replace('.md', '')
        parse_html_dir = os.path.join(HTML_DIR, date)
        if not os.path.exists(parse_html_dir):
            os.makedirs(parse_html_dir, 0755)
        parse_html_file = os.path.join(parse_html_dir, slug)
        with open(parse_html_file, 'w') as f:
            f.write(template.render(
                title = chinese,
                slug = slug,
                content = md_content,
                bodyid = "body",
                who = "小玩子"
                )
                    )

        for_index.update({parse_html_file:[slug, chinese]})

    # generate index html
    template = env.get_template('index.html.jinja2'))
    with open(os.path.join(HTML_DIR, 'index'), 'w') as f:
        f.write(template.render(
            title = "小玩子",
            bodyid = "body",
            content = for_index,
            who = "小玩子"
            )
                )


# URLS
urlpatterns = (
    url(r'^webhook$', webhook.as_view(), name='webhook'),
)

application = get_wsgi_application()


if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


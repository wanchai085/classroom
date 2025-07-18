# D:\classroom\teachers\templatetags\student_extras.py

from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Template filter ที่ใช้สำหรับดึงค่าจาก dictionary ด้วย key ที่เป็นตัวแปร
    การใช้งานใน template: {{ my_dictionary|get_item:my_key }}
    """
    return dictionary.get(key)
from django.contrib.admin import SimpleListFilter
from django.db.models import Q

from ssc.utilities import categories


class CategoryFilter(SimpleListFilter):
    title = 'Категория приоритета'
    parameter_name = 'priority_category'

    def lookups(self, request, model_admin):
        return categories

    def queryset(self, request, queryset):
        if self.value() == 'Category1':
            return queryset.filter(Q(attachmentDeath__gt='') | Q(attachmentDisabled__gt=''))
        if self.value() == 'Category2':
            return queryset.filter(Q(attachmentKandas__gt=''))
        if self.value() == 'Category3':
            return queryset.filter(Q(is_serpin=True))
        if self.value() == 'Category4':
            return queryset.filter(Q(attachmentLarge__gt=''))
        if self.value() == 'NoCategory':
            return queryset.filter(Q(attachmentDeath='') & Q(attachmentDisabled='') & Q(attachmentKandas='')
                                   & Q(attachmentLarge='') & Q(is_serpin=False))

    def to_representation(obj):
        if obj.attachmentDeath != '' or obj.attachmentDisabled != '':
            return categories[0][1]
        if obj.attachmentKandas != '':
            return categories[1][1]
        if obj.is_serpin:
            return categories[2][1]
        if obj.attachmentLarge != '':
            return categories[3][1]
        return categories[4][1]

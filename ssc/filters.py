from django.contrib.admin import SimpleListFilter
from django.db.models import Q


class CategoryFilter(SimpleListFilter):
    title = 'Категория приоритета'
    parameter_name = 'priority_category'

    def lookups(self, request, model_admin):
        return [('Category1', 'Категория 1 (Инвалиды и сироты)'),
                ('Category2', 'Категория 2 (Кандас)'),
                ('Category3', 'Категория 3 (Серпын)'),
                ('Category4', 'Категория 4 (Многодетные)'),
                ('NoCategory', 'На общих основаниях')]

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
import nltk
from math import pi
from collections import Counter
from bokeh.transform import cumsum
from bokeh.layouts import widgetbox, row, column
from bokeh.models import ColumnDataSource, Panel, Legend, LegendItem
from bokeh.models.widgets import TextInput, Select, Paragraph
from bokeh.models import LogColorMapper, LinearColorMapper
from bokeh.palettes import Category20c, Category20_16
from bokeh.palettes import Viridis256 as palette
from bokeh.plotting import figure

from .utils import country_dic


def text_tab(list_of_sp_obj):


    def make_text_data(list_of_sp_obj, country, year):
        year = int(year)
        print(year, country)
        for sp in list_of_sp_obj:
            if (sp.year==year and sp.country in country):
                print('YES')
                # data={'text':[sp.cleaned_sentences]}
                data={'text':sp.list_of_words}
                pie_data = make_pie_data(data)
                return ColumnDataSource(data),ColumnDataSource(pie_data)


    def get_source_text(src):
        text = ' '.join(['{}'.format(t) for t in src.data['text']])
        return ColumnDataSource({'text':[text]})

    def make_text_plot(src):
        txt = get_source_text(src)
        p = Paragraph(text=txt.data['text'][0],width=800,height=400)
        return p

    def update(attr, old, new):
        c_name = country_select.value
        country_combos = [str(sp.year) for sp in list_of_sp_obj if sp.country==c_name ]
        years = sorted(country_combos)
        print(years, type(years))
        select_speech.options = years

    def update_speech(attr, old, new):
        new_text_src, new_pie_src = make_text_data(list_of_sp_obj, country_select.value,
                                      select_speech.value)
        src.data.update(new_text_src.data)
        par.text = ' '.join(['{}'.format(t) for t in src.data['text']])
        pie_src.data.update(new_pie_src.data)


    def make_pie_data(in_data):

        words = in_data['text']
        data = dict()
        total_counts = len(words)
        data['pos_types'] = ['CD','DT','EX','FW','IN','JJ','MD','NN','PRP','RB','VB']
        data['word_types'] = ['Cardinal Date', 'Determinant','Existential','Foreign Word',
                              'Preposition', 'Adjective', 'Modal', 'Noun', 'Personal Pronoun',
                              'Adverb', 'Verb']
        data['counts'] = [0,0,0,0,0,0,0,0,0,0,0]

        positioned_words = nltk.pos_tag(words)
        # print(positioned_words)
        for pos in positioned_words:
            for ii,type in enumerate(data['pos_types']):
                if type in pos[1]:
                    data['counts'][ii] += 1

        other_counts = total_counts - sum(data['counts'])
        data['pos_types'].append('other')
        data['word_types'].append('other')
        data['counts'].append(other_counts)

        # NOTE: this is wrt the most common ones. TDOD change!
        # total_counts = sum(data['counts'])
        data['angle'] = [i/total_counts*2*pi for i in data['counts']]
        data['color'] = Category20c[len(data['pos_types'])]

        return data


    def make_pie_plot(src):

        p = figure(plot_width=300, plot_height=800, title="Pie Chart",
                   toolbar_location=None, tools="hover",
                   tooltips="@word_types: @counts", x_range=(-0.5, 1.0))

        r = p.wedge(x=0, y=1, radius=0.4,
                start_angle=cumsum('angle', include_zero=True),
                end_angle=cumsum('angle'),
                line_color="white", fill_color='color',
                # legend='word_types', source=src)
                source=src)


        legend = Legend(items=[LegendItem(label=dict(field="word_types"),
                        renderers=[r])], location=(0, 30))
        p.add_layout(legend, 'below')
        p.axis.axis_label = None
        p.axis.visible = False
        p.grid.grid_line_color = None

        return p




    country_select = Select(title="Option:", value="FRA",
                            options=list(country_dic.keys()))
    country_select.on_change('value', update)

    select_speech = Select(title="Speech:", value="1970",options=None)
    # select_speech = Select(title="Speech:")
    select_speech.on_change('value', update_speech)

    src,pie_src = make_text_data(list_of_sp_obj, country_select.value, select_speech.value)

    par = make_text_plot(src)
    pie = make_pie_plot(pie_src)

    # Put controls in a single element
    controls = widgetbox(country_select, select_speech)

    # Create a row layout
    layout = row(column(controls, pie), par)

    # Make a tab with the layout
    tab = Panel(child=layout, title='Speech')

    return tab

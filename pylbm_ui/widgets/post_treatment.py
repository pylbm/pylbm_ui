# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import os
import glob
import hashlib
import json
import h5py

from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import numpy as np

import ipyvuetify as v
import ipywidgets as widgets
import traitlets

from .debug import debug
from ..config import default_path, plot_config, voila_notebook
from ..utils import IntField, FloatField
from ..simulation import Plot
from .pylbmwidget import out

@debug
class FormProperties_1D:
    def __init__(self):
        self.label = v.TextField(label='label', v_model='')
        self.line_style = v.Select(label='Line style', items=[{'text': v, 'value': k} for k, v in Line2D.lineStyles.items()], v_model=plot_config['linestyle'])
        self.line_width = IntField(label='linewidth', v_model=plot_config['linewidth'])
        self.marker = v.Select(label='Marker', items=[{'text': v, 'value': k} for k, v in Line2D.markers.items()], v_model=plot_config['marker'])
        self.marker_size = IntField(label='Marker size', v_model=plot_config['markersize'])
        self.alpha = FloatField(label='alpha', v_model=plot_config['alpha'])
        self.color = v.ColorPicker(v_model=plot_config['colors'][0])

        self.widget = [
            self.label,
            self.line_style,
            self.line_width,
            self.marker,
            self.marker_size,
            self.alpha,
            v.Row(children=[
                self.color
            ],justify='center'),
        ]

@debug
class FormProperties_2D:
    def __init__(self):
        self.label = v.TextField(label='label', v_model='')
        self.min_value = FloatField(label='minimum value')
        self.max_value = FloatField(label='maximum value')

        headers=[
            {'text': 'Name', 'value': 'name'},
            {'text': 'Color', 'value': 'color'}
        ]

        self.cmap = v.ListItemGroup(
            v_model=plt.colormaps().index('RdBu'),
            children=[
                v.ListItem(children=[
                    v.ListItemContent(children=[
                        v.ListItemTitle(children=[name]),
                        v.ListItemSubtitle(children=[
                            v.Img(src=f'pylbm_ui/widgets/cmap/{name}.png', height=30, width=400)
                        ])
                    ])
                ])
            for name in plt.colormaps()
        ])

        self.widget = [
            self.label,
            self.min_value,
            self.max_value,
            v.ExpansionPanels(v_model=None, children=[
                v.ExpansionPanel(children=[
                    v.ExpansionPanelHeader(children=['Colormaps']),
                    v.ExpansionPanelContent(children=[self.cmap])
                ])
            ])
        ]

@debug
class SelectedDataTable(v.VuetifyTemplate):
    template = traitlets.Unicode('''
        <template>
            <div>
                <v-data-table
                    v-model="selected"
                    :show-select="true"
                    :single-select="single_select"
                    :headers="headers"
                    :items="items"
                    item-key="id"
                >
                    <template #item.action="item">
                        <v-btn icon @click="edit_plot_item(item.item)">
                            <v-icon>mdi-pen<v-icon>
                        </v-btn>
                        <v-btn icon @click="remove_item(item.item)">
                            <v-icon>mdi-delete<v-icon>
                        </v-btn>
                    </template>

                </v-data-table>
            </div>
        </template>
    ''').tag(sync=True)

    single_select = traitlets.Bool().tag(sync=True)
    selected = traitlets.List([]).tag(sync=True)
    headers = traitlets.List([]).tag(sync=True)
    items = traitlets.List([]).tag(sync=True)
    properties = traitlets.List([]).tag(sync=True)

    def __init__(self, table, **kwargs):
        self.table = table

        update = v.Btn(children=['update'], color='success')
        close = v.Btn(children=['close'], color='error')

        self.form_1d = FormProperties_1D()
        self.form_2d = FormProperties_2D()

        self.form = v.CardText(children=self.form_1d.widget)

        self.dialog = v.Dialog(
                width='500',
                v_model=False,
                children=[
                    v.Card(children=[
                        v.CardTitle(class_='headline gray lighten-2', primary_title=True, children=[
                            'Plot properties'
                        ]),
                        self.form,
                        v.CardActions(children=[v.Spacer(), update, close])
                ]),
            ])

        def close_btn(widget, event, data):
            self.dialog.v_model = False

        update.on_event('click', self.update_btn)
        close.on_event('click', close_btn)

        super().__init__(**kwargs)

    def vue_edit_plot_item(self, item):
        with out:
            index = self.items.index(item)

            if item['dim'] == 1:
                form = self.form_1d
                form.label.v_model = self.properties[index]['label']
                form.line_width.value  = self.properties[index]['linewidth']
                form.line_style.v_model = self.properties[index]['linestyle']
                form.marker.v_model = self.properties[index]['marker']
                form.marker_size.value   = self.properties[index]['markersize']
                form.alpha.value   = self.properties[index]['alpha']
                form.color.v_model = self.properties[index]['color']
            elif item['dim'] == 2:
                form = self.form_2d
                form.label.v_model = self.properties[index]['label']
                form.min_value.value = self.properties[index]['min_value']
                form.max_value.value = self.properties[index]['max_value']
                form.cmap.v_model = self.properties[index]['cmap']

            self.form.children = form.widget
            self.current_index = index
            self.dialog.v_model = True

    def update_btn(self, widget, event, data):
        index = self.current_index

        if self.items[index]['dim'] == 1:
            form = self.form_1d
            self.properties[index]['label'] = form.label.v_model
            self.properties[index]['linewidth'] = form.line_width.value
            self.properties[index]['linestyle'] = form.line_style.v_model
            self.properties[index]['marker'] = form.marker.v_model
            self.properties[index]['markersize'] = form.marker_size.value
            self.properties[index]['alpha'] = form.alpha.value
            self.properties[index]['color'] = form.color.v_model
        elif self.items[index]['dim'] == 2:
            form = self.form_2d
            self.properties[index]['label'] = form.label.v_model
            self.properties[index]['min_value'] = form.min_value.value
            self.properties[index]['max_value'] = form.max_value.value
            self.properties[index]['cmap'] = form.cmap.v_model

        self.notify_change({'name': 'properties', 'type': 'change'})
        self.dialog.v_model = False


    def vue_remove_item(self, item):
        with out:
            index = self.items.index(item)
            self.properties.pop(index)
            self.items.remove(item)
            self.table.items.append(item)
            self.selected = [i for i in self.selected if item != i]
            self.notify_change({'name': 'items', 'type': 'change'})
            self.table.notify_change({'name': 'items', 'type': 'change'})

@debug
class PostTreatmentWidget:
    def __init__(self):

        self.select_dim = v.Select(label='Dimension', items=[1, 2], v_model=1)
        self.previous_dim = 1

        headers=[
            {'text': 'Id', 'value': 'id'},
            {'text': 'Iteration', 'value': 'iteration'},
            {'text': 'Time', 'value': 'time' },
            {'text': 'Field', 'value': 'field' },
            {'text': 'Model', 'value': 'model' },
            {'text': 'Test case', 'value': 'test case' },
            {'text': 'LB scheme', 'value': 'lb scheme' },
            {'text': 'Filename', 'value':'file' },
            {'text': 'Directory', 'value': 'directory' },
        ]

        headers_select = v.Select(label='Show columns',
                                  items=[{'text': v['text'], 'value': i+1} for i, v in enumerate(headers[1:])],
                                  v_model=list(range(1, 7)),
                                  multiple=True)

        search = v.TextField(
            v_model=None,
            append_icon="mdi-magnify",
            label="Search",
            single_line=True,
            hide_details=True,
        )

        self.table = v.DataTable(
            v_model=[],
            headers=[headers[i] for i in headers_select.v_model],
            items=[],
            item_key="id",
            single_select=False,
            show_select=True,
            search='',
        )

        self.selected_cache = [[]]*3
        self.select_item_cache = [[]]*3
        self.properties_cache = [[]]*3
        self.select_table = SelectedDataTable(self.table,
            headers=[headers[i] for i in headers_select.v_model] + [{'text': 'Action', 'value': 'action'}],
        )

        self.plot = Plot()

        def select(change):
            with out:
                for e in list(self.table.v_model):
                    self.select_table.items.append(e)
                    if e['dim'] == 1:
                        self.select_table.properties.append({'label': e['field'],
                                                             'color': plot_config['colors'][0],
                                                             'alpha': plot_config['alpha'],
                                                             'linewidth': plot_config['linewidth'],
                                                             'linestyle': plot_config['linestyle'],
                                                             'marker': plot_config['marker'],
                                                             'markersize': plot_config['markersize']
                        })
                    elif e['dim'] == 2:
                        h5 = os.path.join(e['directory'], e['file'])
                        h5_data = h5py.File(h5)
                        data = h5_data[e['field']][:]
                        self.select_table.properties.append({'label': e['field'],
                                                             'min_value': np.nanmin(data),
                                                             'max_value': np.nanmax(data),
                                                             'cmap': plt.colormaps().index(plot_config['cmap'])})
                    self.table.items.remove(e)
                self.table.v_model = []
                self.select_table.notify_change({'name': 'items', 'type': 'change'})
                self.table.notify_change({'name': 'items', 'type': 'change'})

        def search_text(change):
            self.table.search = search.v_model

        # self.update(None)

        self.select_table.observe(self.plot_result, 'items')
        self.select_table.observe(self.plot_result, 'properties')
        self.select_table.observe(self.plot_result, 'selected')
        search.observe(search_text, 'v_model')
        self.table.observe(select, 'v_model')
        self.select_dim.observe(self.cache, 'v_model')

        def update_headers(change):
            with out:
                self.table.headers = [headers[i] for i in headers_select.v_model]
                self.select_table.headers = [headers[i] for i in headers_select.v_model] + [{'text': 'Action', 'value': 'action'}]
                self.select_table.notify_change({'name': 'items', 'type': 'change'})
                self.table.notify_change({'name': 'items', 'type': 'change'})

        headers_select.observe(update_headers, 'v_model')

        download_zip = v.Btn(children=['Download results'])

        def create_zip(widget, event, data):
            from zipfile import ZipFile

            zipfilename = os.path.join(voila_notebook, 'results.zip')
            with ZipFile(zipfilename, 'w') as zipObj:
                for folderName, subfolders, filenames in os.walk(default_path):
                    for filename in filenames:
                        #create complete filepath of file in directory
                        filePath = os.path.join(folderName, filename)

                        # Add file to zip
                        zipObj.write(filePath, filePath.replace(default_path, ''))

            dialog.children = [
                v.Card(children=[
                    v.CardTitle(children=[
                        widgets.HTML(f'<a href="./results.zip" download="results.zip">Download the archive</a>')
                    ])

                ])
            ]
            dialog.v_model = True

        self.title = v.TextField(label='Plot title', v_model='')
        self.xlabel = v.TextField(label='x label', v_model='')
        self.ylabel = v.TextField(label='y label', v_model='')
        self.legend = v.Switch(label='Add legend', v_model=False)

        self.title.observe(self.set_plot_properties, 'v_model')
        self.xlabel.observe(self.set_plot_properties, 'v_model')
        self.ylabel.observe(self.set_plot_properties, 'v_model')
        self.legend.observe(self.set_plot_properties, 'v_model')

        dialog = v.Dialog()
        dialog.v_model = False
        dialog.width = '200'
        download_zip.on_event('click', create_zip)

        self.menu = [
            self.select_dim,
            headers_select,
            self.title,
            self.xlabel,
            self.ylabel,
            self.legend,
            download_zip,
            dialog
        ]
        self.main = [
            v.Card(children=[
                v.CardTitle(children=[
                    'Available results',
                    v.Spacer(),
                    search
                ]),
                self.table,
                ],
                class_='ma-2',
            ),
            v.Card(children=[
                v.CardTitle(children=[
                    'Selected results',
                ]),
                self.select_table, self.select_table.dialog,
                ],
                class_='ma-2',
            ),
            v.Row(children=[self.plot.fig.canvas], justify='center'),
            ]

    def plot_result(self, change):
        with out:
            self.plot.ax.clear()
            if self.plot.color_bar is not None:
                self.plot.color_bar.remove()
                self.plot.color_bar = None
            class Domain:
                pass

            for item in self.select_table.selected:
                index = self.select_table.items.index(item)
                properties = self.select_table.properties[index]
                domain = Domain()
                h5 = os.path.join(item['directory'], item['file'])
                h5_data = h5py.File(h5)
                domain.x = h5_data['x_0'][:]
                domain.dim = 1
                if 'x_1' in h5_data.keys():
                    domain.y = h5_data['x_1'][:]
                    domain.dim = 2
                data = h5_data[item['field']][:]
                time = item['time']
                self.plot.plot_type = None
                self.plot.plot(time, domain, item['field'], data, transpose=False, properties=properties)

            self.set_plot_properties(None)
            self.plot.fig.canvas.draw_idle()

    def set_plot_properties(self, change):
        with out:
            self.plot.ax.title.set_text(f'{self.title.v_model}')
            self.plot.ax.set_xlabel(f'{self.xlabel.v_model}')
            self.plot.ax.set_ylabel(f'{self.ylabel.v_model}')

            handles, labels = self.plot.ax.get_legend_handles_labels()
            if handles:
                if self.legend.v_model:
                    self.plot.ax.legend()
                else:
                    self.plot.ax.legend().remove()
            self.plot.fig.canvas.draw_idle()

    def cache(self, change):
        if self.select_dim.v_model == 1:
            self.legend.class_ = ''
        else:
            self.legend.class_ = 'd-none'

        self.selected_cache[self.previous_dim - 1] = [i for i in self.select_table.selected]
        self.select_item_cache[self.previous_dim - 1] = [i for i in self.select_table.items]
        self.properties_cache[self.previous_dim - 1] = [i for i in self.select_table.properties]

        self.previous_dim = self.select_dim.v_model
        self.select_table.selected = self.selected_cache[self.select_dim.v_model - 1]
        self.select_table.items = self.select_item_cache[self.select_dim.v_model - 1]
        self.select_table.properties = self.properties_cache[self.select_dim.v_model - 1]

        self.update(None)

    def update(self, change):
        with out:
            data = []

            if self.select_dim.v_model == 1:
                self.select_table.single_select = False
            else:
                self.select_table.single_select = True

            for root, d_names,f_names in os.walk(default_path):
                if 'simu_config.json' in f_names:
                    cfg = json.load(open(root + '/simu_config.json'))
                    if cfg['dim'] == self.select_dim.v_model:
                        dx = cfg['dx']
                        la = cfg['lb_scheme']['args']['la']
                        dt = dx/la
                        h5files = glob.glob(root + '/*.h5')
                        for h5 in h5files:
                            filename = os.path.basename(h5)
                            dirname = os.path.dirname(os.path.abspath(h5))

                            tmp = os.path.splitext(filename)[0].split('_')
                            if len(tmp) == 2:
                                ite = int(os.path.splitext(filename)[0].split('_')[-1])

                                # check if the h5 file is not used for the save process
                                # which means that the ressource is temporarely unavailable
                                is_available = False
                                while (not is_available):
                                    try:
                                        h5_data = h5py.File(h5)
                                        is_available = True
                                    except OSError:
                                        pass

                                for k in h5_data.keys():
                                    if k not in ['x_0', 'x_1', 'x_2']:
                                        data.append({
                                                    'iteration': ite,
                                                    'dim': cfg['dim'],
                                                    'time': ite*dt,
                                                    'field': k,
                                                    'model': cfg['v_model']['model'],
                                                    'test case': cfg['v_model']['test_case'],
                                                    'lb scheme': cfg['v_model']['lb_scheme'],
                                                    'file': filename,
                                                    'directory': dirname,
                                        })
                                        dhash = hashlib.md5()
                                        encoded = json.dumps(data[-1], sort_keys=True).encode()
                                        dhash.update(encoded)
                                        data[-1]['id'] = dhash.hexdigest()

            items = self.select_table.items
            index = [i for i, item in enumerate(items) if item in data]

            self.select_table.items = [items[i] for i in index]
            self.select_table.properties = [self.select_table.properties[i] for i in index]

            items = self.select_table.selected
            selected = [self.select_table.items.index(item) for item in items if item in self.select_table.items]

            self.table.items = [i for i in data if i not in self.select_table.items]
            self.select_table.selected = [self.select_table.items[i] for i in selected]

            self.select_table.notify_change({'name': 'items', 'type': 'change'})
            self.table.notify_change({'name': 'items', 'type': 'change'})

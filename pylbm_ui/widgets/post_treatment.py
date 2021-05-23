# Authors:
#     Loic Gouarin <loic.gouarin@polytechnique.edu>
#     Benjamin Graille <benjamin.graille@universite-paris-saclay.fr>
#     Thibaut Van Hoof <thibaut.vanhoof@cenaero.be>
#
# License: BSD 3 clause

import os
import glob
import json
import h5py

from matplotlib.lines import Line2D

import ipyvuetify as v

from ..config import default_path, plot_config
from ..utils import IntField, FloatField
from ..simulation import Plot
from .pylbmwidget import out

import ipyvuetify as v
import traitlets

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
    palette = traitlets.List([]).tag(sync=True)

    def __init__(self, table, **kwargs):
        self.table = table

        update = v.Btn(children=['update'])
        close = v.Btn(children=['close'])

        self.form = [IntField(label='linewidth', v_model=plot_config['linewidth']),
                     v.Select(label='Line style', items=[{'text': v, 'value': k} for k, v in Line2D.lineStyles.items()], v_model=plot_config['linestyle']),
                     v.Select(label='Marker', items=[{'text': v, 'value': k} for k, v in Line2D.markers.items()], v_model=plot_config['marker']),
                     IntField(label='Marker size', v_model=plot_config['markersize']),
                     FloatField(label='alpha', v_model=plot_config['alpha']),
                     v.ColorPicker(v_model=plot_config['colors'][0]),
        ]

        self.dialog = v.Dialog(
                width='500',
                v_model=False,
                children=[
                    v.Card(children=[
                        v.CardTitle(class_='headline gray lighten-2', primary_title=True, children=[
                            'Plot properties'
                        ]),
                        v.CardText(children=self.form),
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
            self.form[0].value  = self.palette[index]['linewidth']
            self.form[1].v_model = self.palette[index]['linestyle']
            self.form[2].v_model = self.palette[index]['marker']
            self.form[3].value   = self.palette[index]['markersize']
            self.form[4].value   = self.palette[index]['alpha']
            self.form[5].v_model = self.palette[index]['color']
            self.current_index = index
            self.dialog.v_model = True

    def update_btn(self, widget, event, data):
        index = self.current_index
        self.palette[index]['linewidth'] = self.form[0].value
        self.palette[index]['linestyle'] = self.form[1].v_model
        self.palette[index]['marker'] = self.form[2].v_model
        self.palette[index]['markersize'] = self.form[3].value
        self.palette[index]['alpha'] = self.form[4].value
        self.palette[index]['color'] = self.form[5].v_model
        self.notify_change({'name': 'palette', 'type': 'change'})
        self.dialog.v_model = False


    def vue_remove_item(self, item):
        with out:
            index = self.items.index(item)
            self.palette.pop(index)
            self.items.remove(item)
            self.table.items.append(item)
            self.selected = [i for i in self.selected if item != i]
            self.notify_change({'name': 'items', 'type': 'change'})
            self.table.notify_change({'name': 'items', 'type': 'change'})

class PostTreatmentWidget:
    def __init__(self):

        self.select_dim = v.Select(label='Dimension', items=[1, 2], v_model=1)
        self.previous_dim = 1

        headers=[
            {'text': 'Iteration', 'value': 'iteration'},
            {'text': 'Time', 'value': 'time' },
            {'text': 'Field', 'value': 'field' },
            {'text': 'Test case', 'value': 'test case' },
            {'text': 'LB scheme', 'value': 'lb scheme' },
            {'text': 'Filename', 'value':'file' },
            {'text': 'Directory', 'value': 'directory' },
        ]

        headers_select = v.Select(label='Show columns',
                                  items=[{'text': v['text'], 'value': i} for i, v in enumerate(headers)],
                                  v_model=list(range(5)),
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
        self.palette_cache = [[]]*3
        self.select_table = SelectedDataTable(self.table,
            headers=[headers[i] for i in headers_select.v_model] + [{'text': 'Action', 'value': 'action'}],
        )

        self.plot = Plot()

        def select(change):
            with out:
                for e in list(self.table.v_model):
                    self.select_table.items.append(e)
                    self.select_table.palette.append({'color': plot_config['colors'][0],
                                                      'alpha': plot_config['alpha'],
                                                      'linewidth': plot_config['linewidth'],
                                                      'linestyle': plot_config['linestyle'],
                                                      'marker': plot_config['marker'],
                                                      'markersize': plot_config['markersize']
                    })
                    self.table.items.remove(e)
                self.table.v_model = []
                self.select_table.notify_change({'name': 'items', 'type': 'change'})
                self.table.notify_change({'name': 'items', 'type': 'change'})

        def search_text(change):
            self.table.search = search.v_model

        self.update(None)

        self.select_table.observe(self.plot_result, 'items')
        self.select_table.observe(self.plot_result, 'palette')
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
            import webbrowser
            import tempfile

            zipdir = tempfile.TemporaryDirectory().name
            if not os.path.exists(zipdir):
                os.makedirs(zipdir)
            zipfilename = os.path.join(zipdir, 'results.zip')
            with ZipFile(zipfilename, 'w') as zipObj:
                for folderName, subfolders, filenames in os.walk(default_path):
                    for filename in filenames:
                        #create complete filepath of file in directory
                        filePath = os.path.join(folderName, filename)

                        # Add file to zip
                        zipObj.write(filePath, filePath.replace(default_path, ''))

            webbrowser.open(f'file://{zipfilename}')

        download_zip.on_event('click', create_zip)

        self.menu = [self.select_dim, headers_select, download_zip]
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
            # out
            ]

    def plot_result(self, change):
        with out:
            self.plot.ax.clear()
            if self.plot.color_bar is not None:
                self.plot.color_bar.remove()
                self.plot.color_bar = None
            class Domain:
                pass

            for item, palette in zip(self.select_table.selected, self.select_table.palette):
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
                self.plot.plot(time, domain, item['field'], data, transpose=False, palette=palette)
            self.plot.fig.canvas.draw_idle()

    def cache(self, change):
        self.selected_cache[self.previous_dim - 1] = [i for i in self.select_table.selected]
        self.select_item_cache[self.previous_dim - 1] = [i for i in self.select_table.items]
        self.palette_cache[self.previous_dim - 1] = [i for i in self.select_table.palette]

        self.previous_dim = self.select_dim.v_model
        self.select_table.selected = self.selected_cache[self.select_dim.v_model - 1]
        self.select_table.items = self.select_item_cache[self.select_dim.v_model - 1]
        self.select_table.palette = self.palette_cache[self.select_dim.v_model - 1]

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

                            ite = int(os.path.splitext(h5)[0].split('_')[-1])

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
                                    data.append({'iteration': ite,
                                                'time': ite*dt,
                                                'field': k,
                                                'test case': cfg['test_case']['class'],
                                                'lb scheme': cfg['lb_scheme']['class'],
                                                'file': filename,
                                                'directory': dirname,
                                    })

            items = [{k: v for k, v in item.items() if k != 'id'} for item in self.select_table.items]
            index = [i for i, item in enumerate(items) if item in data]

            self.select_table.items = [items[i] for i in index]
            self.select_table.palette = [self.select_table.palette[i] for i in index]

            items = [{k: v for k, v in item.items() if k != 'id'} for item in self.select_table.selected]
            selected = [self.select_table.items.index(item) for item in items if item in self.select_table.items]

            self.table.items = [i for i in data if i not in self.select_table.items]

            # add Id
            id = 0
            for i in range(len(self.table.items)):
                self.table.items[i]['id'] = id
                id += 1

            for i in range(len(self.select_table.items)):
                self.select_table.items[i]['id'] = id
                id += 1

            self.select_table.selected = [self.select_table.items[i] for i in selected]

            self.select_table.notify_change({'name': 'items', 'type': 'change'})
            self.table.notify_change({'name': 'items', 'type': 'change'})

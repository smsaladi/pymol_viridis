'''
For further detail/future revisions, visit 
https://shyam.saladi.org/pymol_viridis

DESCRIPTION
    Makes perceptually uniform and colorblind accessible color palettes
    available in PyMOL

    Certain colors are indistinguishable to people with the various forms of
    color blindness, and therefore are better not used in figures intended for
    public viewing. This script provides additional color palettes to allow for
    an alternative to the default rainbow coloring that is unambiguous both to
    colorblind and non-colorblind people.

    By running this script,
        * default color palette for `spectrum` is changed to turbo
        * viridis options are added to menus.

    Color scale details:
        - viridis, magma, inferno, plasma: Stéfan van der Walt, Nathaniel Smith,
            & Eric Firing. https://bids.github.io/colormap
        - cividis: Jamie Nuñez, Christopher Anderton, Ryan Renslow.
                    https://doi.org/10.1371/journal.pone.0199239
        - turbo: Anton Mikhailov.
                https://ai.googleblog.com/2019/08/turbo-improved-rainbow-colormap-for.html
    
    Pymol script colorblindfriendly.py by @jaredsampson used as reference for modifying menus:
        https://github.com/Pymol-Scripts/Pymol-script-repo/blob/master/colorblindfriendly.py

USAGE

    Simply run this script. 
    To unpatch `spectrum` and remove viridis menus from graphical interface,
    run `remove_viridis_menus()`.

REQUIREMENTS

    The new menus (`add_viridis_menus()` and `remove_viridis_menus()`)
    require PyMOL 1.6.0 or later.

AUTHOR

    Shyam Saladi
    Github: @smsaladi

LICENSE (MIT)

Copyright (c) 2019 Shyam Saladi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.


Palette RGB values is taken from bokeh.palettes.
Corresponding copyrights notices can be found here:
https://github.com/bokeh/bokeh/blob/b19f2c5/bokeh/palettes.py

'''
from __future__ import print_function, division

__author__ = 'Shyam Saladi'
__version__ = '0.0.1'

import pymol
from pymol import cmd

'''Add/configure palettes used by `spectrum`
'''

def patch_spectrum():
    '''Monkey-patches spectrum to set the default palette to `turbo`
    '''
    spectrum_defaults = list(cmd.spectrum.__defaults__)
    spectrum_defaults[1] = 'turbo'
    cmd.spectrum.__defaults__ = tuple(spectrum_defaults)
    return

def unpatch_spectrum():
    '''Resets default color palette to `rainbow`
    '''
    spectrum_defaults = list(cmd.spectrum.__defaults__)
    spectrum_defaults[1] = 'rainbow'
    cmd.spectrum.__defaults__ = tuple(spectrum_defaults)
    return

def viridis(*args, **kwargs):
    '''New command to color using viridis
    '''
    if len(args) >= 1:
        args = list(args)
        args[1] = 'viridis'
    else:
        kwargs['palette'] = 'viridis'
    cmd.spectrum(*args, **kwargs)
cmd.extend(viridis)


def add_palettes():
    '''Add the color blind-friendly colormaps/palettes to PyMOL.'''
    def format_colors(values):
        return ' '.join(values).replace('#', '0x')

    for pal_name, values in NEW_PALETTES.items():
        pymol.viewing.palette_colors_dict[pal_name] = format_colors(values)

    # Notify user of newly available colors
    print('`' + '`, `'.join(NEW_PALETTES.keys()) + '`')
    return


'''Add Viridis options to menus

Under `C` menu:
    Adds to menus: `by_chain` & `auto`
        - Does this by monkey-patching the current menus
    Creates a new menu: `viridis` (like `spectrum`)

Some parts adapted from
https://github.com/schrodinger/pymol-open-source/blob/6ca016e82a5cf9febc064ee5a15ab505d51ec8c7/modules/pymol/menu.py

'''

def _viridis_menu(self_cmd, sele):
    viridis_col = _colorize_text('viridis')

    r = [
        [2, 'Viridis:', ''],
        [1, viridis_col + '(elem C)',
            'cmd.spectrum("count", "viridis", selection="('+sele+') & elem C")'   ],
        [1, viridis_col + '(*/CA)'  ,
            'cmd.spectrum("count", "viridis", selection="('+sele+') & */CA")'     ],
        [1, viridis_col             ,
            'cmd.spectrum("count", "viridis", selection="'+sele+'", byres=1)'     ],
        [0, '', ''],
        [1, 'b-factors'             ,
            'cmd.spectrum("b", "viridis", selection=("'+sele+'"), quiet=0)'       ],
        [1, 'b-factors(*/CA)'       ,
            'cmd.spectrum("b", "viridis", selection="(('+sele+') & */CA)", quiet=0)'],
        [0, '', ''],
        [1, 'area (molecular)'      ,
            'util.color_by_area(("'+sele+'"), "molecular", palette="viridis")'    ],
        [1, 'area (solvent)'        ,
            'util.color_by_area(("'+sele+'"), "solvent", palette="viridis")'      ],
        ]
    with pymol.menu.menucontext(self_cmd, sele) as mc:
        r += [
            [0, '', ''],
            [1, 'user properties', [[ 2, 'User Properties:', '' ]] + [
                [ 1, key, [[ 2, 'Palette', '' ]] + [
                    [1, palette, 'cmd.spectrum("properties[%s]", "%s", "%s")' % (repr(key), palette, sele)]
                    for palette in ('viridis', 'blue white red', 'green red')
                ]] for key in mc.props
            ]],
        ]
    return r


def _by_chain_patch(self_cmd, sele):
    by_chain_col = _colorize_text('by chain')
    by_segi_col = _colorize_text('by segi ')
    chainbows_col = _colorize_text('chainbows')
    
    r = pymol.menu._by_chain(self_cmd, sele) + [
        [0, '', ''],
        [0, '', ''],
        [1, by_chain_col + '(elem C)',
            'util.color_chains("('+sele+' and elem C)", palette="viridis", _self=cmd)'],
        [1, by_chain_col + '(*/CA)',
            'util.color_chains("('+sele+' and name CA)", palette="viridis", _self=cmd)'],
        [1, by_chain_col,
            'util.color_chains("('+sele+')", palette="viridis", _self=cmd)'],
        [0, '', ''],
        [1, chainbows_col,
            'util.chainbow("('+sele+')", palette="viridis", _self=cmd)'],
        [0, '', ''],
        [1, by_segi_col + '(elem C)',
            'cmd.spectrum("segi", "viridis", "('+sele+') & elem C")'],
        [1, by_segi_col,
            'cmd.spectrum("segi", "viridis", "' + sele + '")'],
        ]
    return r

def _color_auto_patch(self_cmd, sele):
    by_obj_col = _colorize_text('by obj')
    by_obj_c_col = _colorize_text('by obj(elem C)')
    chainbows_col = _colorize_text('chainbows')
    r = pymol.menu._color_auto(self_cmd, sele) + [
        [ 0, '', ''],
        [ 1, by_obj_col,
          'util.color_objs("('+sele+' and elem C)", palette="viridis", _self=cmd)'],
        [ 1, by_obj_c_col,
          'util.color_objs("('+sele+')", palette="viridis", _self=cmd)'],
        ]
    return r

def _mol_color_patch(self_cmd, sele):
    viridis_col = _colorize_text('viridis')
    with pymol.menu.menucontext(self_cmd, sele):
        for i, item in enumerate(pymol.menu._mol_color(self_cmd, sele)):
            _, text, _ = item
            if text == 'auto':
                auto_menu_idx = i
                break
        
        r = pymol.menu._mol_color(self_cmd, sele)
        r.insert(auto_menu_idx - 1, [1, viridis_col, _viridis_menu(self_cmd, sele)])
        return r

def _has_viridis_palettes():
    for k in NEW_PALETTES.keys():
        if k not in pymol.viewing.palette_colors_dict.keys():
            return False
    return True

def add_viridis_menus():
    '''Add viridis options to the PyMOL OpenGL menus where spectrum options exist
    '''

    if hasattr(pymol.menu, 'has_viridis_menus') and pymol.menu.has_viridis_menus:
        print('Palette menus were already added!')
        return

    # Make sure palettes are installed.
    if not _has_viridis_palettes():
        print('Adding palettes...')
        add_palettes()

    print('Changing default palette for spectrum to `turbo`')
    patch_spectrum()

    # Abort if PyMOL is too old.
    try:
        from pymol.menu import all_colors_list
    except ImportError:
        print('PyMOL version too old for palettes menus. Requires 1.6.0 or later.')
        return
    
    # These will each be monkey-patched
    pymol.menu._by_chain = pymol.menu.by_chain
    pymol.menu._mol_color = pymol.menu.mol_color
    pymol.menu._color_auto = pymol.menu.color_auto

    # Add the menu
    print('Adding viridis to menus...')
    pymol.menu.by_chain = _by_chain_patch
    pymol.menu.mol_color = _mol_color_patch
    pymol.menu.color_auto = _color_auto_patch

    pymol.menu.has_viridis_menus = True
    print('Done!')

    return

def remove_viridis_menus():
    '''Removes viridis options to the PyMOL OpenGL menus
    '''

    print('Changing default palette for spectrum back to `rainbow`')
    unpatch_spectrum()

    if not hasattr(pymol.menu, 'has_viridis_menus') or not pymol.menu.has_viridis_menus:
        print('Palette menus are not present!')
        return

    # Abort if PyMOL is too old.
    try:
        from pymol.menu import all_colors_list
    except ImportError:
        print('PyMOL version too old for palettes menus. Requires 1.6.0 or later.')
        return

    print('Removing viridis from menus...')
    pymol.menu.by_chain = pymol.menu._by_chain
    pymol.menu.mol_color = pymol.menu._mol_color
    pymol.menu.color_auto = pymol.menu._color_auto

    pymol.menu.has_viridis_menus = False
    print('Done!')

    return


'''Help with generating colorized text for menus

\\RGB represents colors in 'decimal' format, i.e. 0-9 for R, 0-9 for G, 0-9 for B.
This function converts 16-bit hex colors `#RRGGBB` into this format. It was initially
used, but for efficency the \\RGB values are hard coded below
'''
def _convert_hex_color(color):
    chex = chex[1:]
    rgb = cmd.get_color_tuple('0x' + chex)
    rgb = [str(int(v * 9)) for v in rgb]
    rgb = ''.join(rgb)
    return rgb

# last 8 for viridis10 (first two are too dark -- hard to see text on black background)
# _viridis8 = ['#3E4989', '#30678D', '#25828E', '#1E9C89', '#35B778', '#6BCD59', '#B2DD2C', '#FDE724']
# viridis8_rgb = [_convert_hex_color(c) for c in _viridis8]
_viridis8_rgb = ['224', '134', '145', '154', '164', '373', '671', '881']

def _colorize_text(text, palette=tuple(_viridis8_rgb)):
    '''Colorizes text given a list of RGB color values (NNN format)
    '''
    text = list(text)
    palette = list(palette)
    
    palette.append(888) # last character white again
    palette = palette[:min(len(palette), len(text))]
    for i, col in enumerate(palette):
        if text[i] == '(':
            text[i] = '\\%s%s' % ('888', text[i])
            break
        text[i] = '\\%s%s' % (col, text[i])

    return ''.join(text) + '\\888'

'''The HEX values are from bokeh.palettes
https://github.com/bokeh/bokeh/blob/b19f2c5547024bdc288d02e73fdb65e65991df5f/bokeh/palettes.py
'''
NEW_PALETTES = {
    'inferno': [
        '#000003', '#000004', '#000006', '#010007', '#010109', '#01010B', '#02010E', '#020210', '#030212', '#040314', '#040316', '#050418',
        '#06041B', '#07051D', '#08061F', '#090621', '#0A0723', '#0B0726', '#0D0828', '#0E082A', '#0F092D', '#10092F', '#120A32', '#130A34',
        '#140B36', '#160B39', '#170B3B', '#190B3E', '#1A0B40', '#1C0C43', '#1D0C45', '#1F0C47', '#200C4A', '#220B4C', '#240B4E', '#260B50',
        '#270B52', '#290B54', '#2B0A56', '#2D0A58', '#2E0A5A', '#300A5C', '#32095D', '#34095F', '#350960', '#370961', '#390962', '#3B0964',
        '#3C0965', '#3E0966', '#400966', '#410967', '#430A68', '#450A69', '#460A69', '#480B6A', '#4A0B6A', '#4B0C6B', '#4D0C6B', '#4F0D6C',
        '#500D6C', '#520E6C', '#530E6D', '#550F6D', '#570F6D', '#58106D', '#5A116D', '#5B116E', '#5D126E', '#5F126E', '#60136E', '#62146E',
        '#63146E', '#65156E', '#66156E', '#68166E', '#6A176E', '#6B176E', '#6D186E', '#6E186E', '#70196E', '#72196D', '#731A6D', '#751B6D',
        '#761B6D', '#781C6D', '#7A1C6D', '#7B1D6C', '#7D1D6C', '#7E1E6C', '#801F6B', '#811F6B', '#83206B', '#85206A', '#86216A', '#88216A',
        '#892269', '#8B2269', '#8D2369', '#8E2468', '#902468', '#912567', '#932567', '#952666', '#962666', '#982765', '#992864', '#9B2864',
        '#9C2963', '#9E2963', '#A02A62', '#A12B61', '#A32B61', '#A42C60', '#A62C5F', '#A72D5F', '#A92E5E', '#AB2E5D', '#AC2F5C', '#AE305B',
        '#AF315B', '#B1315A', '#B23259', '#B43358', '#B53357', '#B73456', '#B83556', '#BA3655', '#BB3754', '#BD3753', '#BE3852', '#BF3951',
        '#C13A50', '#C23B4F', '#C43C4E', '#C53D4D', '#C73E4C', '#C83E4B', '#C93F4A', '#CB4049', '#CC4148', '#CD4247', '#CF4446', '#D04544',
        '#D14643', '#D24742', '#D44841', '#D54940', '#D64A3F', '#D74B3E', '#D94D3D', '#DA4E3B', '#DB4F3A', '#DC5039', '#DD5238', '#DE5337',
        '#DF5436', '#E05634', '#E25733', '#E35832', '#E45A31', '#E55B30', '#E65C2E', '#E65E2D', '#E75F2C', '#E8612B', '#E9622A', '#EA6428',
        '#EB6527', '#EC6726', '#ED6825', '#ED6A23', '#EE6C22', '#EF6D21', '#F06F1F', '#F0701E', '#F1721D', '#F2741C', '#F2751A', '#F37719',
        '#F37918', '#F47A16', '#F57C15', '#F57E14', '#F68012', '#F68111', '#F78310', '#F7850E', '#F8870D', '#F8880C', '#F88A0B', '#F98C09',
        '#F98E08', '#F99008', '#FA9107', '#FA9306', '#FA9506', '#FA9706', '#FB9906', '#FB9B06', '#FB9D06', '#FB9E07', '#FBA007', '#FBA208',
        '#FBA40A', '#FBA60B', '#FBA80D', '#FBAA0E', '#FBAC10', '#FBAE12', '#FBB014', '#FBB116', '#FBB318', '#FBB51A', '#FBB71C', '#FBB91E',
        '#FABB21', '#FABD23', '#FABF25', '#FAC128', '#F9C32A', '#F9C52C', '#F9C72F', '#F8C931', '#F8CB34', '#F8CD37', '#F7CF3A', '#F7D13C',
        '#F6D33F', '#F6D542', '#F5D745', '#F5D948', '#F4DB4B', '#F4DC4F', '#F3DE52', '#F3E056', '#F3E259', '#F2E45D', '#F2E660', '#F1E864',
        '#F1E968', '#F1EB6C', '#F1ED70', '#F1EE74', '#F1F079', '#F1F27D', '#F2F381', '#F2F485', '#F3F689', '#F4F78D', '#F5F891', '#F6FA95',
        '#F7FB99', '#F9FC9D', '#FAFDA0', '#FCFEA4'],

    'magma': [
        '#000003', '#000004', '#000006', '#010007', '#010109', '#01010B', '#02020D', '#02020F', '#030311', '#040313', '#040415', '#050417',
        '#060519', '#07051B', '#08061D', '#09071F', '#0A0722', '#0B0824', '#0C0926', '#0D0A28', '#0E0A2A', '#0F0B2C', '#100C2F', '#110C31',
        '#120D33', '#140D35', '#150E38', '#160E3A', '#170F3C', '#180F3F', '#1A1041', '#1B1044', '#1C1046', '#1E1049', '#1F114B', '#20114D',
        '#221150', '#231152', '#251155', '#261157', '#281159', '#2A115C', '#2B115E', '#2D1060', '#2F1062', '#301065', '#321067', '#341068',
        '#350F6A', '#370F6C', '#390F6E', '#3B0F6F', '#3C0F71', '#3E0F72', '#400F73', '#420F74', '#430F75', '#450F76', '#470F77', '#481078',
        '#4A1079', '#4B1079', '#4D117A', '#4F117B', '#50127B', '#52127C', '#53137C', '#55137D', '#57147D', '#58157E', '#5A157E', '#5B167E',
        '#5D177E', '#5E177F', '#60187F', '#61187F', '#63197F', '#651A80', '#661A80', '#681B80', '#691C80', '#6B1C80', '#6C1D80', '#6E1E81',
        '#6F1E81', '#711F81', '#731F81', '#742081', '#762181', '#772181', '#792281', '#7A2281', '#7C2381', '#7E2481', '#7F2481', '#812581',
        '#822581', '#842681', '#852681', '#872781', '#892881', '#8A2881', '#8C2980', '#8D2980', '#8F2A80', '#912A80', '#922B80', '#942B80',
        '#952C80', '#972C7F', '#992D7F', '#9A2D7F', '#9C2E7F', '#9E2E7E', '#9F2F7E', '#A12F7E', '#A3307E', '#A4307D', '#A6317D', '#A7317D',
        '#A9327C', '#AB337C', '#AC337B', '#AE347B', '#B0347B', '#B1357A', '#B3357A', '#B53679', '#B63679', '#B83778', '#B93778', '#BB3877',
        '#BD3977', '#BE3976', '#C03A75', '#C23A75', '#C33B74', '#C53C74', '#C63C73', '#C83D72', '#CA3E72', '#CB3E71', '#CD3F70', '#CE4070',
        '#D0416F', '#D1426E', '#D3426D', '#D4436D', '#D6446C', '#D7456B', '#D9466A', '#DA4769', '#DC4869', '#DD4968', '#DE4A67', '#E04B66',
        '#E14C66', '#E24D65', '#E44E64', '#E55063', '#E65162', '#E75262', '#E85461', '#EA5560', '#EB5660', '#EC585F', '#ED595F', '#EE5B5E',
        '#EE5D5D', '#EF5E5D', '#F0605D', '#F1615C', '#F2635C', '#F3655C', '#F3675B', '#F4685B', '#F56A5B', '#F56C5B', '#F66E5B', '#F6705B',
        '#F7715B', '#F7735C', '#F8755C', '#F8775C', '#F9795C', '#F97B5D', '#F97D5D', '#FA7F5E', '#FA805E', '#FA825F', '#FB8460', '#FB8660',
        '#FB8861', '#FB8A62', '#FC8C63', '#FC8E63', '#FC9064', '#FC9265', '#FC9366', '#FD9567', '#FD9768', '#FD9969', '#FD9B6A', '#FD9D6B',
        '#FD9F6C', '#FDA16E', '#FDA26F', '#FDA470', '#FEA671', '#FEA873', '#FEAA74', '#FEAC75', '#FEAE76', '#FEAF78', '#FEB179', '#FEB37B',
        '#FEB57C', '#FEB77D', '#FEB97F', '#FEBB80', '#FEBC82', '#FEBE83', '#FEC085', '#FEC286', '#FEC488', '#FEC689', '#FEC78B', '#FEC98D',
        '#FECB8E', '#FDCD90', '#FDCF92', '#FDD193', '#FDD295', '#FDD497', '#FDD698', '#FDD89A', '#FDDA9C', '#FDDC9D', '#FDDD9F', '#FDDFA1',
        '#FDE1A3', '#FCE3A5', '#FCE5A6', '#FCE6A8', '#FCE8AA', '#FCEAAC', '#FCECAE', '#FCEEB0', '#FCF0B1', '#FCF1B3', '#FCF3B5', '#FCF5B7',
        '#FBF7B9', '#FBF9BB', '#FBFABD', '#FBFCBF'],

'plasma': [
        '#0C0786', '#100787', '#130689', '#15068A', '#18068B', '#1B068C', '#1D068D', '#1F058E', '#21058F', '#230590', '#250591', '#270592',
        '#290593', '#2B0594', '#2D0494', '#2F0495', '#310496', '#330497', '#340498', '#360498', '#380499', '#3A049A', '#3B039A', '#3D039B',
        '#3F039C', '#40039C', '#42039D', '#44039E', '#45039E', '#47029F', '#49029F', '#4A02A0', '#4C02A1', '#4E02A1', '#4F02A2', '#5101A2',
        '#5201A3', '#5401A3', '#5601A3', '#5701A4', '#5901A4', '#5A00A5', '#5C00A5', '#5E00A5', '#5F00A6', '#6100A6', '#6200A6', '#6400A7',
        '#6500A7', '#6700A7', '#6800A7', '#6A00A7', '#6C00A8', '#6D00A8', '#6F00A8', '#7000A8', '#7200A8', '#7300A8', '#7500A8', '#7601A8',
        '#7801A8', '#7901A8', '#7B02A8', '#7C02A7', '#7E03A7', '#7F03A7', '#8104A7', '#8204A7', '#8405A6', '#8506A6', '#8607A6', '#8807A5',
        '#8908A5', '#8B09A4', '#8C0AA4', '#8E0CA4', '#8F0DA3', '#900EA3', '#920FA2', '#9310A1', '#9511A1', '#9612A0', '#9713A0', '#99149F',
        '#9A159E', '#9B179E', '#9D189D', '#9E199C', '#9F1A9B', '#A01B9B', '#A21C9A', '#A31D99', '#A41E98', '#A51F97', '#A72197', '#A82296',
        '#A92395', '#AA2494', '#AC2593', '#AD2692', '#AE2791', '#AF2890', '#B02A8F', '#B12B8F', '#B22C8E', '#B42D8D', '#B52E8C', '#B62F8B',
        '#B7308A', '#B83289', '#B93388', '#BA3487', '#BB3586', '#BC3685', '#BD3784', '#BE3883', '#BF3982', '#C03B81', '#C13C80', '#C23D80',
        '#C33E7F', '#C43F7E', '#C5407D', '#C6417C', '#C7427B', '#C8447A', '#C94579', '#CA4678', '#CB4777', '#CC4876', '#CD4975', '#CE4A75',
        '#CF4B74', '#D04D73', '#D14E72', '#D14F71', '#D25070', '#D3516F', '#D4526E', '#D5536D', '#D6556D', '#D7566C', '#D7576B', '#D8586A',
        '#D95969', '#DA5A68', '#DB5B67', '#DC5D66', '#DC5E66', '#DD5F65', '#DE6064', '#DF6163', '#DF6262', '#E06461', '#E16560', '#E26660',
        '#E3675F', '#E3685E', '#E46A5D', '#E56B5C', '#E56C5B', '#E66D5A', '#E76E5A', '#E87059', '#E87158', '#E97257', '#EA7356', '#EA7455',
        '#EB7654', '#EC7754', '#EC7853', '#ED7952', '#ED7B51', '#EE7C50', '#EF7D4F', '#EF7E4E', '#F0804D', '#F0814D', '#F1824C', '#F2844B',
        '#F2854A', '#F38649', '#F38748', '#F48947', '#F48A47', '#F58B46', '#F58D45', '#F68E44', '#F68F43', '#F69142', '#F79241', '#F79341',
        '#F89540', '#F8963F', '#F8983E', '#F9993D', '#F99A3C', '#FA9C3B', '#FA9D3A', '#FA9F3A', '#FAA039', '#FBA238', '#FBA337', '#FBA436',
        '#FCA635', '#FCA735', '#FCA934', '#FCAA33', '#FCAC32', '#FCAD31', '#FDAF31', '#FDB030', '#FDB22F', '#FDB32E', '#FDB52D', '#FDB62D',
        '#FDB82C', '#FDB92B', '#FDBB2B', '#FDBC2A', '#FDBE29', '#FDC029', '#FDC128', '#FDC328', '#FDC427', '#FDC626', '#FCC726', '#FCC926',
        '#FCCB25', '#FCCC25', '#FCCE25', '#FBD024', '#FBD124', '#FBD324', '#FAD524', '#FAD624', '#FAD824', '#F9D924', '#F9DB24', '#F8DD24',
        '#F8DF24', '#F7E024', '#F7E225', '#F6E425', '#F6E525', '#F5E726', '#F5E926', '#F4EA26', '#F3EC26', '#F3EE26', '#F2F026', '#F2F126',
        '#F1F326', '#F0F525', '#F0F623', '#EFF821'],

'viridis': [
        '#440154', '#440255', '#440357', '#450558', '#45065A', '#45085B', '#46095C', '#460B5E', '#460C5F', '#460E61', '#470F62', '#471163',
        '#471265', '#471466', '#471567', '#471669', '#47186A', '#48196B', '#481A6C', '#481C6E', '#481D6F', '#481E70', '#482071', '#482172',
        '#482273', '#482374', '#472575', '#472676', '#472777', '#472878', '#472A79', '#472B7A', '#472C7B', '#462D7C', '#462F7C', '#46307D',
        '#46317E', '#45327F', '#45347F', '#453580', '#453681', '#443781', '#443982', '#433A83', '#433B83', '#433C84', '#423D84', '#423E85',
        '#424085', '#414186', '#414286', '#404387', '#404487', '#3F4587', '#3F4788', '#3E4888', '#3E4989', '#3D4A89', '#3D4B89', '#3D4C89',
        '#3C4D8A', '#3C4E8A', '#3B508A', '#3B518A', '#3A528B', '#3A538B', '#39548B', '#39558B', '#38568B', '#38578C', '#37588C', '#37598C',
        '#365A8C', '#365B8C', '#355C8C', '#355D8C', '#345E8D', '#345F8D', '#33608D', '#33618D', '#32628D', '#32638D', '#31648D', '#31658D',
        '#31668D', '#30678D', '#30688D', '#2F698D', '#2F6A8D', '#2E6B8E', '#2E6C8E', '#2E6D8E', '#2D6E8E', '#2D6F8E', '#2C708E', '#2C718E',
        '#2C728E', '#2B738E', '#2B748E', '#2A758E', '#2A768E', '#2A778E', '#29788E', '#29798E', '#287A8E', '#287A8E', '#287B8E', '#277C8E',
        '#277D8E', '#277E8E', '#267F8E', '#26808E', '#26818E', '#25828E', '#25838D', '#24848D', '#24858D', '#24868D', '#23878D', '#23888D',
        '#23898D', '#22898D', '#228A8D', '#228B8D', '#218C8D', '#218D8C', '#218E8C', '#208F8C', '#20908C', '#20918C', '#1F928C', '#1F938B',
        '#1F948B', '#1F958B', '#1F968B', '#1E978A', '#1E988A', '#1E998A', '#1E998A', '#1E9A89', '#1E9B89', '#1E9C89', '#1E9D88', '#1E9E88',
        '#1E9F88', '#1EA087', '#1FA187', '#1FA286', '#1FA386', '#20A485', '#20A585', '#21A685', '#21A784', '#22A784', '#23A883', '#23A982',
        '#24AA82', '#25AB81', '#26AC81', '#27AD80', '#28AE7F', '#29AF7F', '#2AB07E', '#2BB17D', '#2CB17D', '#2EB27C', '#2FB37B', '#30B47A',
        '#32B57A', '#33B679', '#35B778', '#36B877', '#38B976', '#39B976', '#3BBA75', '#3DBB74', '#3EBC73', '#40BD72', '#42BE71', '#44BE70',
        '#45BF6F', '#47C06E', '#49C16D', '#4BC26C', '#4DC26B', '#4FC369', '#51C468', '#53C567', '#55C666', '#57C665', '#59C764', '#5BC862',
        '#5EC961', '#60C960', '#62CA5F', '#64CB5D', '#67CC5C', '#69CC5B', '#6BCD59', '#6DCE58', '#70CE56', '#72CF55', '#74D054', '#77D052',
        '#79D151', '#7CD24F', '#7ED24E', '#81D34C', '#83D34B', '#86D449', '#88D547', '#8BD546', '#8DD644', '#90D643', '#92D741', '#95D73F',
        '#97D83E', '#9AD83C', '#9DD93A', '#9FD938', '#A2DA37', '#A5DA35', '#A7DB33', '#AADB32', '#ADDC30', '#AFDC2E', '#B2DD2C', '#B5DD2B',
        '#B7DD29', '#BADE27', '#BDDE26', '#BFDF24', '#C2DF22', '#C5DF21', '#C7E01F', '#CAE01E', '#CDE01D', '#CFE11C', '#D2E11B', '#D4E11A',
        '#D7E219', '#DAE218', '#DCE218', '#DFE318', '#E1E318', '#E4E318', '#E7E419', '#E9E419', '#ECE41A', '#EEE51B', '#F1E51C', '#F3E51E',
        '#F6E61F', '#F8E621', '#FAE622', '#FDE724'],

'cividis': [
        '#00204C', '#00204E', '#002150', '#002251', '#002353', '#002355', '#002456', '#002558', '#00265A', '#00265B', '#00275D', '#00285F',
        '#002861', '#002963', '#002A64', '#002A66', '#002B68', '#002C6A', '#002D6C', '#002D6D', '#002E6E', '#002E6F', '#002F6F', '#002F6F',
        '#00306F', '#00316F', '#00316F', '#00326E', '#00336E', '#00346E', '#00346E', '#01356E', '#06366E', '#0A376D', '#0E376D', '#12386D',
        '#15396D', '#17396D', '#1A3A6C', '#1C3B6C', '#1E3C6C', '#203C6C', '#223D6C', '#243E6C', '#263E6C', '#273F6C', '#29406B', '#2B416B',
        '#2C416B', '#2E426B', '#2F436B', '#31446B', '#32446B', '#33456B', '#35466B', '#36466B', '#37476B', '#38486B', '#3A496B', '#3B496B',
        '#3C4A6B', '#3D4B6B', '#3E4B6B', '#404C6B', '#414D6B', '#424E6B', '#434E6B', '#444F6B', '#45506B', '#46506B', '#47516B', '#48526B',
        '#49536B', '#4A536B', '#4B546B', '#4C556B', '#4D556B', '#4E566B', '#4F576C', '#50586C', '#51586C', '#52596C', '#535A6C', '#545A6C',
        '#555B6C', '#565C6C', '#575D6D', '#585D6D', '#595E6D', '#5A5F6D', '#5B5F6D', '#5C606D', '#5D616E', '#5E626E', '#5F626E', '#5F636E',
        '#60646E', '#61656F', '#62656F', '#63666F', '#64676F', '#65676F', '#666870', '#676970', '#686A70', '#686A70', '#696B71', '#6A6C71',
        '#6B6D71', '#6C6D72', '#6D6E72', '#6E6F72', '#6F6F72', '#6F7073', '#707173', '#717273', '#727274', '#737374', '#747475', '#757575',
        '#757575', '#767676', '#777776', '#787876', '#797877', '#7A7977', '#7B7A77', '#7B7B78', '#7C7B78', '#7D7C78', '#7E7D78', '#7F7E78',
        '#807E78', '#817F78', '#828078', '#838178', '#848178', '#858278', '#868378', '#878478', '#888578', '#898578', '#8A8678', '#8B8778',
        '#8C8878', '#8D8878', '#8E8978', '#8F8A78', '#908B78', '#918C78', '#928C78', '#938D78', '#948E78', '#958F78', '#968F77', '#979077',
        '#989177', '#999277', '#9A9377', '#9B9377', '#9C9477', '#9D9577', '#9E9676', '#9F9776', '#A09876', '#A19876', '#A29976', '#A39A75',
        '#A49B75', '#A59C75', '#A69C75', '#A79D75', '#A89E74', '#A99F74', '#AAA074', '#ABA174', '#ACA173', '#ADA273', '#AEA373', '#AFA473',
        '#B0A572', '#B1A672', '#B2A672', '#B4A771', '#B5A871', '#B6A971', '#B7AA70', '#B8AB70', '#B9AB70', '#BAAC6F', '#BBAD6F', '#BCAE6E',
        '#BDAF6E', '#BEB06E', '#BFB16D', '#C0B16D', '#C1B26C', '#C2B36C', '#C3B46C', '#C5B56B', '#C6B66B', '#C7B76A', '#C8B86A', '#C9B869',
        '#CAB969', '#CBBA68', '#CCBB68', '#CDBC67', '#CEBD67', '#D0BE66', '#D1BF66', '#D2C065', '#D3C065', '#D4C164', '#D5C263', '#D6C363',
        '#D7C462', '#D8C561', '#D9C661', '#DBC760', '#DCC860', '#DDC95F', '#DECA5E', '#DFCB5D', '#E0CB5D', '#E1CC5C', '#E3CD5B', '#E4CE5B',
        '#E5CF5A', '#E6D059', '#E7D158', '#E8D257', '#E9D356', '#EBD456', '#ECD555', '#EDD654', '#EED753', '#EFD852', '#F0D951', '#F1DA50',
        '#F3DB4F', '#F4DC4E', '#F5DD4D', '#F6DE4C', '#F7DF4B', '#F9E049', '#FAE048', '#FBE147', '#FCE246', '#FDE345', '#FFE443', '#FFE542',
        '#FFE642', '#FFE743', '#FFE844', '#FFE945'],

'turbo': [
        '#30123b', '#311542', '#32184a', '#341b51', '#351e58', '#36215f', '#372365', '#38266c', '#392972', '#3a2c79', '#3b2f7f', '#3c3285',
        '#3c358b', '#3d3791', '#3e3a96', '#3f3d9c', '#4040a1', '#4043a6', '#4145ab', '#4148b0', '#424bb5', '#434eba', '#4350be', '#4353c2',
        '#4456c7', '#4458cb', '#455bce', '#455ed2', '#4560d6', '#4563d9', '#4666dd', '#4668e0', '#466be3', '#466de6', '#4670e8', '#4673eb',
        '#4675ed', '#4678f0', '#467af2', '#467df4', '#467ff6', '#4682f8', '#4584f9', '#4587fb', '#4589fc', '#448cfd', '#438efd', '#4291fe',
        '#4193fe', '#4096fe', '#3f98fe', '#3e9bfe', '#3c9dfd', '#3ba0fc', '#39a2fc', '#38a5fb', '#36a8f9', '#34aaf8', '#33acf6', '#31aff5',
        '#2fb1f3', '#2db4f1', '#2bb6ef', '#2ab9ed', '#28bbeb', '#26bde9', '#25c0e6', '#23c2e4', '#21c4e1', '#20c6df', '#1ec9dc', '#1dcbda',
        '#1ccdd7', '#1bcfd4', '#1ad1d2', '#19d3cf', '#18d5cc', '#18d7ca', '#17d9c7', '#17dac4', '#17dcc2', '#17debf', '#18e0bd', '#18e1ba',
        '#19e3b8', '#1ae4b6', '#1be5b4', '#1de7b1', '#1ee8af', '#20e9ac', '#22eba9', '#24eca6', '#27eda3', '#29eea0', '#2cef9d', '#2ff09a',
        '#32f197', '#35f394', '#38f491', '#3bf48d', '#3ff58a', '#42f687', '#46f783', '#4af880', '#4df97c', '#51f979', '#55fa76', '#59fb72',
        '#5dfb6f', '#61fc6c', '#65fc68', '#69fd65', '#6dfd62', '#71fd5f', '#74fe5c', '#78fe59', '#7cfe56', '#80fe53', '#84fe50', '#87fe4d',
        '#8bfe4b', '#8efe48', '#92fe46', '#95fe44', '#98fe42', '#9bfd40', '#9efd3e', '#a1fc3d', '#a4fc3b', '#a6fb3a', '#a9fb39', '#acfa37',
        '#aef937', '#b1f836', '#b3f835', '#b6f735', '#b9f534', '#bbf434', '#bef334', '#c0f233', '#c3f133', '#c5ef33', '#c8ee33', '#caed33',
        '#cdeb34', '#cfea34', '#d1e834', '#d4e735', '#d6e535', '#d8e335', '#dae236', '#dde036', '#dfde36', '#e1dc37', '#e3da37', '#e5d838',
        '#e7d738', '#e8d538', '#ead339', '#ecd139', '#edcf39', '#efcd39', '#f0cb3a', '#f2c83a', '#f3c63a', '#f4c43a', '#f6c23a', '#f7c039',
        '#f8be39', '#f9bc39', '#f9ba38', '#fab737', '#fbb537', '#fbb336', '#fcb035', '#fcae34', '#fdab33', '#fda932', '#fda631', '#fda330',
        '#fea12f', '#fe9e2e', '#fe9b2d', '#fe982c', '#fd952b', '#fd9229', '#fd8f28', '#fd8c27', '#fc8926', '#fc8624', '#fb8323', '#fb8022',
        '#fa7d20', '#fa7a1f', '#f9771e', '#f8741c', '#f7711b', '#f76e1a', '#f66b18', '#f56817', '#f46516', '#f36315', '#f26014', '#f15d13',
        '#ef5a11', '#ee5810', '#ed550f', '#ec520e', '#ea500d', '#e94d0d', '#e84b0c', '#e6490b', '#e5460a', '#e3440a', '#e24209', '#e04008',
        '#de3e08', '#dd3c07', '#db3a07', '#d93806', '#d73606', '#d63405', '#d43205', '#d23005', '#d02f04', '#ce2d04', '#cb2b03', '#c92903',
        '#c72803', '#c52602', '#c32402', '#c02302', '#be2102', '#bb1f01', '#b91e01', '#b61c01', '#b41b01', '#b11901', '#ae1801', '#ac1601',
        '#a91501', '#a61401', '#a31201', '#a01101', '#9d1001', '#9a0e01', '#970d01', '#940c01', '#910b01', '#8e0a01', '#8b0901', '#870801',
        '#840701', '#810602', '#7d0502', '#7a0402']
}


if __name__ == 'pymol':
    add_viridis_menus()

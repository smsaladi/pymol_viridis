
"""
Generate a screenshot preview (some mouse work necessary...)

Assuming this is downloaded
wget https://files.rcsb.org/download/1rh5.pdb1.gz


"""
cmd.bg_color('white')
cmd.set('orthoscopic')

cmd.fetch("1rh5")
cmd.color("magenta")

cmd.set('grid_mode', 1)
cmd.set('grid_max', 6)

cmd.run('viridispalettes.py')

for i, p in enumerate(['rainbow', 'turbo', 'viridis']):
    name = "1rh5_" + p
    cmd.copy(name, "1rh5")
    cmd.copy(name + '_b', "1rh5")

    sele = '*/CA & ' + name
    cmd.spectrum('count', p, 'chain A & ' + sele)
    cmd.set('grid_slot', i + 1, name)

    cmd.spectrum('b', p, sele + '_b')
    cmd.set('grid_slot', i + 4, name + '_b')


cmd.delete("1rh5")

cmd.set_view((
     0.218785018,    0.973232150,    0.070372909,
    -0.946494520,    0.194132715,    0.257793516,
     0.237230048,   -0.123009682,    0.963633597,
     0.000000000,    0.000000000, -220.784698486,
    40.937301636,   49.316246033,   16.465759277,
  -21095.009765625, 21536.578125000,   20.000000000 ))

cmd.save("preview.pse")
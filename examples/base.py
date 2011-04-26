def render_example(render_object, name):
    render_object.export_stl('./'+name+'.stl')
    print "Source:"
    print render_object.to_source()
    print ""
    
    render_object.render()
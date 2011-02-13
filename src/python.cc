#include "openscad.h"
#include "MainWindow.h"
#include "node.h"
#include "module.h"
#include "context.h"
#include "value.h"
#include "export.h"
#include "builtin.h"
#include "expression.h"

#include <QApplication>


struct Arg{
	char *name;
	char valueType;
	int vecLen;
	union{
		double dblValue;
		const char* strValue;
		double *vecValue;
	};
};

Context *root_context;

extern "C" ModuleInstantiation* inst_module(const char* name, int numargs, Arg* args, int numchildren, ModuleInstantiation **children){
	ModuleInstantiation *mod = new ModuleInstantiation();
	mod->modname = QString(name);
	int i;
	for (i=0; i<numargs; i++){
		Arg* arg = &args[i];
		Expression* a = new Expression();
		a->type = "C";
		printf("arg %i: %c\n", i, arg->valueType);
		if (arg->valueType=='d'){
			printf("double val: %f\n", arg->dblValue);
			a->const_value = new Value(arg->dblValue);
		}else if(arg->valueType=='v'){
			printf("vec val of length %i\n", arg->vecLen);
			a->const_value = new Value();
			a->const_value->type = Value::VECTOR;
			for (int i=0; i<arg->vecLen; i++){
				printf("\tvec[%i] = %f\n", i, arg->vecValue[i]);
				Value *v = new Value(arg->vecValue[i]);
				a->const_value->vec.append(v);
			}
		}else{
			printf("Unknown value type: %c!\n", arg->valueType);
		}
		mod->argexpr.append(a);
		if (arg->name){
			mod->argnames.append(QString(arg->name));
			printf("Named\n");
		}else{
			printf("Unnamed\n");
			mod->argnames.append(QString());
		}
	}
	
	for (i=0; i<numchildren; i++){
		mod->children.append(children[i]);
	}
	return mod;
} 

Context *make_root_context(){
	Context *root_ctx = new Context();
	
	root_ctx->functions_p = &builtin_functions;
	root_ctx->modules_p = &builtin_modules;
	root_ctx->set_variable("$fn", Value(0.0));
	root_ctx->set_variable("$fs", Value(1.0));
	root_ctx->set_variable("$fa", Value(12.0));
	root_ctx->set_variable("$t", Value(0.0));

	Value zero3;
	zero3.type = Value::VECTOR;
	zero3.vec.append(new Value(0.0));
	zero3.vec.append(new Value(0.0));
	zero3.vec.append(new Value(0.0));
	root_ctx->set_variable("$vpt", zero3);
	root_ctx->set_variable("$vpr", zero3);
	
	return root_ctx;
}

AbstractNode *find_root_tag(AbstractNode *n)
{
	foreach(AbstractNode *v, n->children) {
		if (v->modinst->tag_root) return v;
		if (AbstractNode *vroot = find_root_tag(v)) return vroot;
	}
	return NULL;
}


AbstractNode *compileModuleInstantiation(ModuleInstantiation *root_module_inst){
	AbstractNode *absolute_root_node, *root_node; 
	absolute_root_node = root_module_inst->evaluate(root_context);
	
	if (!absolute_root_node)
		return NULL;

	// Do we have an explicit root node (! modifier)?
	if (!(root_node = find_root_tag(absolute_root_node))) {
		root_node = absolute_root_node;
	}
	
	return root_node;
}

CGAL_Nef_polyhedron *compileCGAL(AbstractNode *root_node){
	return new CGAL_Nef_polyhedron(root_node->render_cgal_nef_polyhedron());
}

extern "C" void render(ModuleInstantiation *mod){
	bool useGUI = true;
	int argc = 1;
	char *argv1 = "openscad";
	char **argv = &argv1;
	
	QApplication app(argc, argv, useGUI);
	
	QString qfilename;
	
	MainWindow *m = new MainWindow(qfilename);
	
	// Hide console, editor by default
	m->viewActionHide->setChecked(true);
	m->editActionHide->setChecked(true);
	m->editor->hide();
	m->console->hide();
	
	AbstractNode *root_node = compileModuleInstantiation(mod);
	m->renderNode(root_node);

	app.connect(m, SIGNAL(destroyed()), &app, SLOT(quit()));
	app.exec();
}

extern "C" const char *export_dxf(ModuleInstantiation *mod, const char * filename){
	AbstractNode *node = compileModuleInstantiation(mod);
	CGAL_Nef_polyhedron *cgal = compileCGAL(node);

	if (cgal->dim != 2) {
		return "Current top level object is not a 2D object.";
	}

	export_dxf(cgal, filename, NULL);
	return 0;
}

extern "C" const char *export_stl(ModuleInstantiation *mod, const char * filename){
	AbstractNode *node = compileModuleInstantiation(mod);
	CGAL_Nef_polyhedron *cgal = compileCGAL(node);
	
	if (cgal->dim != 3) {
		return "Current top level object is not a 3D object.";
	}

	if (!cgal->p3.is_simple()) {
		return "Object isn't a valid 2-manifold! Modify your design..";
	}
	
	export_stl(cgal, filename, NULL);
	return 0;
}

extern "C" const char *to_source(ModuleInstantiation *mod){
	return mod->dump("").toUtf8();
}

extern "C" void init(){
	initialize_builtin_functions();
	initialize_builtin_modules();
	root_context = make_root_context();
}

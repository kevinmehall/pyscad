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


extern "C" void render(ModuleInstantiation *mod){
	bool useGUI = true;
	int argc = 1;
	char *argv1 = "openscad";
	char **argv = &argv1;
	
	initialize_builtin_functions();
	initialize_builtin_modules();
	
	QApplication app(argc, argv, useGUI);
	
	QString qfilename;
	
	MainWindow *m = new MainWindow(qfilename);
	
	// Hide console, editor by default
	m->viewActionHide->setChecked(true);
	m->editActionHide->setChecked(true);
	m->editor->hide();
	m->console->hide();
	
	m->renderModuleInstantiaton(mod);
	
	app.connect(m, SIGNAL(destroyed()), &app, SLOT(quit()));
	app.exec();
}

#ifndef NODE_H_
#define NODE_H_

#include <QCache>
#include <QVector>

#include "traverser.h"

extern int progress_report_count;
extern void (*progress_report_f)(const class AbstractNode*, void*, int);
extern void *progress_report_vp;

void progress_report_prep(AbstractNode *root, void (*f)(const class AbstractNode *node, void *vp, int mark), void *vp);
void progress_report_fin();

/*!  

	The node tree is the result of evaluation of a module instantiation
	tree.  Both the module tree and the node tree are regenerated from
	scratch for each compile.

 */
class AbstractNode
{
	// FIXME: the idx_counter/idx is mostly (only?) for debugging.
	// We can hash on pointer value or smth. else.
  //  -> remove and
	// use smth. else to display node identifier in CSG tree output?
	static size_t idx_counter;   // Node instantiation index
public:
	AbstractNode(const class ModuleInstantiation *mi);
	virtual ~AbstractNode();
  virtual Response accept(class State &state, class Visitor &visitor) const;
	virtual std::string toString() const;
	/*! The 'OpenSCAD name' of this node, defaults to classname, but can be 
	    overloaded to provide specialization for e.g. CSG nodes, primitive nodes etc.
	    Used for human-readable output. */
	virtual std::string name() const;

  // FIXME: Make return value a reference
	const std::list<AbstractNode*> getChildren() const { 
		return this->children.toList().toStdList(); 
	}
	size_t index() const { return this->idx; }

	static void resetIndexCounter() { idx_counter = 1; }

	// FIXME: Rewrite to STL container?
	// FIXME: Make protected
	QVector<AbstractNode*> children;
	const ModuleInstantiation *modinst;

	// progress_mark is a running number used for progress indication
	// FIXME: Make all progress handling external, put it in the traverser class?
	int progress_mark;
	void progress_prepare();
	void progress_report() const;

	int idx; // Node index (unique per tree)
};

class AbstractIntersectionNode : public AbstractNode
{
public:
	AbstractIntersectionNode(const ModuleInstantiation *mi) : AbstractNode(mi) { };
	virtual ~AbstractIntersectionNode() { };
  virtual Response accept(class State &state, class Visitor &visitor) const;
	virtual std::string toString() const;
	virtual std::string name() const;
};

class AbstractPolyNode : public AbstractNode
{
public:
	AbstractPolyNode(const ModuleInstantiation *mi) : AbstractNode(mi) { };
	virtual ~AbstractPolyNode() { };
  virtual Response accept(class State &state, class Visitor &visitor) const;

	enum render_mode_e {
		RENDER_CGAL,
		RENDER_OPENCSG
	};
  /*! Should return a PolySet of the given geometry. It's normal to return an
		  empty PolySet if smth. is wrong, but don't return NULL unless we change the calling
			strategy for this method. */
	virtual class PolySet *render_polyset(render_mode_e mode, class PolySetRenderer *renderer) const = 0;
};

std::ostream &operator<<(std::ostream &stream, const AbstractNode &node);

#endif

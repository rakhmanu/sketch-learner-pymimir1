
#pragma once

#include <vector>
#include <ostream>
#include <fs/core/problem_info.hxx>
#include <fs/core/actions/actions.hxx>
#include <fs/core/actions/action_id.hxx>
#include <boost/units/detail/utility.hpp>

namespace fs0 {

class Problem;

//! Print a plan
class PlanPrinter {
protected:
	const ActionPlan& _plan;
public:
	PlanPrinter(const ActionPlan& plan) : _plan(plan) {}

	//! Prints a representation of the state to the given stream.
	friend std::ostream& operator<<(std::ostream &os, const PlanPrinter& o) { return o.print(os); }
	std::ostream& print(std::ostream& os) const;

	//! static helpers
	static void print(const std::vector<GroundAction::IdType>& plan, std::ostream& out);
	static void print_json(const std::vector<GroundAction::IdType>& plan, std::ostream& out);
	static void print_json(const std::vector<std::string>& plan, std::ostream& out);
};


namespace print {

class plan {
	protected:
		const plan_t& _plan;

	public:
		plan(const plan_t& plan_) : _plan(plan_) {}

		friend std::ostream& operator<<(std::ostream &os, const plan& o) { return o.print(os); }
		std::ostream& print(std::ostream& os) const;
};


//! Print the proper, demangled name of a std::type_info / std::type_index object
template <typename T>
std::string type_info_name(const T& type) { return boost::units::detail::demangle(type.name()); }

}

} // namespaces
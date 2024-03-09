(define (problem DLOG-4-4-4)
	(:domain driverlog)
	(:objects
	driver1 - driver
	driver2 - driver
	driver3 - driver
	driver4 - driver
	truck1 - truck
	truck2 - truck
	truck3 - truck
	truck4 - truck
	package1 - obj
	package2 - obj
	package3 - obj
	package4 - obj
	s0 - location
	s1 - location
	s2 - location
	s3 - location
	s4 - location
	p0-2 - location
	p0-3 - location
	p0-4 - location
	p2-0 - location
	p3-0 - location
	p3-2 - location
	p4-1 - location
	p4-2 - location
	)
	(:init
	(at driver1 s4)
	(at driver2 s0)
	(at driver3 s2)
	(at driver4 s3)
	(at truck1 s3)
	(empty truck1)
	(at truck2 s4)
	(empty truck2)
	(at truck3 s4)
	(empty truck3)
	(at truck4 s3)
	(empty truck4)
	(at package1 s1)
	(at package2 s4)
	(at package3 s0)
	(at package4 s3)
	(path s0 p0-2)
	(path p0-2 s0)
	(path s2 p0-2)
	(path p0-2 s2)
	(path s0 p0-3)
	(path p0-3 s0)
	(path s3 p0-3)
	(path p0-3 s3)
	(path s0 p0-4)
	(path p0-4 s0)
	(path s4 p0-4)
	(path p0-4 s4)
	(path s3 p3-2)
	(path p3-2 s3)
	(path s2 p3-2)
	(path p3-2 s2)
	(path s4 p4-1)
	(path p4-1 s4)
	(path s1 p4-1)
	(path p4-1 s1)
	(path s4 p4-2)
	(path p4-2 s4)
	(path s2 p4-2)
	(path p4-2 s2)
	(link s0 s1)
	(link s1 s0)
	(link s0 s2)
	(link s2 s0)
	(link s1 s2)
	(link s2 s1)
	(link s2 s3)
	(link s3 s2)
	(link s2 s4)
	(link s4 s2)
	(link s3 s0)
	(link s0 s3)
	(link s3 s4)
	(link s4 s3)
	(link s4 s0)
	(link s0 s4)
)
	(:goal (and
	(at driver1 s3)
	(at driver2 s1)
	(at driver3 s0)
	(at truck1 s1)
	(at truck2 s0)
	(at truck3 s0)
	(at package1 s4)
	(at package2 s4)
	(at package3 s4)
	(at package4 s4)
	))


)

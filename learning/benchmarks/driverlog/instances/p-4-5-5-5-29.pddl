(define (problem DLOG-4-5-5)
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
	truck5 - truck
	package1 - obj
	package2 - obj
	package3 - obj
	package4 - obj
	package5 - obj
	s0 - location
	s1 - location
	s2 - location
	s3 - location
	s4 - location
	p0-1 - location
	p0-3 - location
	p0-4 - location
	p2-0 - location
	p2-1 - location
	p3-1 - location
	p4-2 - location
	)
	(:init
	(at driver1 s4)
	(at driver2 s3)
	(at driver3 s4)
	(at driver4 s4)
	(at truck1 s0)
	(empty truck1)
	(at truck2 s0)
	(empty truck2)
	(at truck3 s3)
	(empty truck3)
	(at truck4 s0)
	(empty truck4)
	(at truck5 s4)
	(empty truck5)
	(at package1 s2)
	(at package2 s0)
	(at package3 s4)
	(at package4 s0)
	(at package5 s2)
	(path s0 p0-1)
	(path p0-1 s0)
	(path s1 p0-1)
	(path p0-1 s1)
	(path s0 p0-3)
	(path p0-3 s0)
	(path s3 p0-3)
	(path p0-3 s3)
	(path s0 p0-4)
	(path p0-4 s0)
	(path s4 p0-4)
	(path p0-4 s4)
	(path s2 p2-0)
	(path p2-0 s2)
	(path s0 p2-0)
	(path p2-0 s0)
	(path s2 p2-1)
	(path p2-1 s2)
	(path s1 p2-1)
	(path p2-1 s1)
	(path s3 p3-1)
	(path p3-1 s3)
	(path s1 p3-1)
	(path p3-1 s1)
	(path s4 p4-2)
	(path p4-2 s4)
	(path s2 p4-2)
	(path p4-2 s2)
	(link s1 s2)
	(link s2 s1)
	(link s1 s3)
	(link s3 s1)
	(link s2 s0)
	(link s0 s2)
	(link s2 s3)
	(link s3 s2)
	(link s2 s4)
	(link s4 s2)
	(link s3 s0)
	(link s0 s3)
	(link s4 s0)
	(link s0 s4)
)
	(:goal (and
	(at driver1 s2)
	(at driver3 s0)
	(at driver4 s4)
	(at truck1 s3)
	(at truck2 s3)
	(at truck3 s4)
	(at truck4 s1)
	(at truck5 s0)
	(at package1 s2)
	(at package2 s1)
	(at package3 s0)
	(at package4 s4)
	(at package5 s3)
	))


)

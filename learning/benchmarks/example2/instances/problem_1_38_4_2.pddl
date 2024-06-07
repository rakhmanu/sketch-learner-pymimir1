(define (problem p01)
  (:domain ulzhal)
(:objects 
      down - direction 
      left - direction 
      right - direction 
      up - direction 
      robot - thing 
      block01 - thing 
      pos0 - location
      pos1 - location
      pos2 - location
      pos3 - location
      pos4 - location
      pos5 - location
      pos6 - location
      pos7 - location
)
 (:init
   (at robot pos7)
   (at block01 pos6)
   (clear pos0)
   (clear pos1)
   (clear pos2)
   (clear pos3)
   (clear pos4)
   (clear pos5)

   (is-goal pos3)
   (is-nongoal pos0)
   (is-nongoal pos1)
   (is-nongoal pos2)
   (is-nongoal pos4)
   (is-nongoal pos5)
   (is-nongoal pos6)
   (is-nongoal pos7)

   (is-agent robot)
   (is-block block01)
   (move-dir pos0 pos4 down)
   (move-dir pos0 pos1 right)
   (move-dir pos1 pos5 down)
   (move-dir pos1 pos0 left)
   (move-dir pos1 pos2 right)
   (move-dir pos2 pos6 down)
   (move-dir pos2 pos1 left)
   (move-dir pos2 pos3 right)
   (move-dir pos3 pos7 down)
   (move-dir pos3 pos2 left)
   (move-dir pos4 pos0 up)
   (move-dir pos4 pos5 right)
   (move-dir pos5 pos1 up)
   (move-dir pos5 pos4 left)
   (move-dir pos5 pos6 right)
   (move-dir pos6 pos2 up)
   (move-dir pos6 pos5 left)
   (move-dir pos6 pos7 right)
   (move-dir pos7 pos3 up)
   (move-dir pos7 pos6 left)
 )
 (:goal (and (at-goal block01) ))
)
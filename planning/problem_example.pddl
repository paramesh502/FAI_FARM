(define (problem farm-scenario-1)
  (:domain farm-operations)
  
  (:objects
    plot1 plot2 plot3 plot4 - plot
    plough1 - ploughing-agent
    sow1 - sowing-agent
    water1 - watering-agent
    harvest1 - harvesting-agent
    drone1 - drone-agent
    wheat corn - crop
  )
  
  (:init
    ; Agent initial positions
    (at plough1 plot1)
    (at sow1 plot1)
    (at water1 plot1)
    (at harvest1 plot1)
    (at drone1 plot1)
    
    ; All agents idle
    (agent-idle plough1)
    (agent-idle sow1)
    (agent-idle water1)
    (agent-idle harvest1)
    (agent-idle drone1)
    
    ; Plot initial states
    (plot-state-initial plot1)
    (plot-state-initial plot2)
    (plot-state-initial plot3)
    (plot-state-initial plot4)
    
    ; Plot adjacency (grid layout)
    (adjacent plot1 plot2)
    (adjacent plot2 plot1)
    (adjacent plot1 plot3)
    (adjacent plot3 plot1)
    (adjacent plot2 plot4)
    (adjacent plot4 plot2)
    (adjacent plot3 plot4)
    (adjacent plot4 plot3)
  )
  
  (:goal
    (and
      ; Goal: Prepare plots for harvest
      (plot-state-ready plot2)
      (plot-state-ready plot3)
      (crop-planted wheat plot2)
      (crop-planted corn plot3)
    )
  )
)

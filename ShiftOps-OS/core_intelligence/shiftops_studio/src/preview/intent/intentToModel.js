import { rampModel } from "../models/rampModel"
import { carModel } from "../models/carModel"
import { breakwallModel } from "../models/breakwallModel"
import { systemModel } from "../models/systemModel"

export function intentToModel(prompt){

  if (!prompt) return systemModel;
  
  const p = prompt.toLowerCase()

  if(p.includes("ramp"))
    return rampModel

  if(p.includes("car"))
    return carModel

  if(p.includes("breakwall") || p.includes("levee") || p.includes("ocean"))
    return breakwallModel

  return systemModel

}

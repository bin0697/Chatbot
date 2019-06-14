# Define the INIT state
INIT = 0
# Define the CHOOSE_COFFEE state
CHOOSE_COFFEE = 1
# Define the ORDERED state
ORDERED = 2
# Define the policy rules
policy_rules = {
    (INIT, "ask_explanation"): (INIT, "I'm a bot to help you order coffee beans"),
    (INIT, "order"): (CHOOSE_COFFEE, "ok, Colombian or Kenyan?"),
    (CHOOSE_COFFEE, "specify_coffee"): (ORDERED, "perfect, the beans are on their way!"),
    (CHOOSE_COFFEE, "ask_explanation"): (CHOOSE_COFFEE, "We have two kinds of coffee beans - the Kenyan ones make a slightly sweeter coffee, and cost $6. The Brazilian beans make a nutty coffee and cost $5.")    
}

for intenn, dataa in policy_rules:
  if dataa == "order":
    print (intenn)
    print (dataa)
    print (policy_rules[intenn,dataa])
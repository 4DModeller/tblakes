# Load required libraries
library(INLA)

# Load CSV file
data <- read.csv("repos/tblakes/data_for_4dm.csv")

# Create mesh based on latitude and longitude coordinates
mesh <- inla.mesh.2d(data$centroid_lon, data$centroid_lat, max.edge = 4)

# Create formula for regression model
formula <- lake_growth ~ ENDO + precip + f(mesh, model = "ar1", group = "year")

# Create fixed effects matrix
fixed_effects <- model.matrix(formula, data = data)

# Create spatial effect using mesh
spatial_effect <- inla.spde2.pcmatern(mesh, alpha = c(2, 2))

# Combine fixed effects and spatial effect
model_formula <- cbind(fixed_effects, spatial_effect)

# Fit the model using INLA
model <- inla(formula = model_formula, data = data, family = "gaussian"
              , control.predictor = list(compute = TRUE))

# Print the model summary
summary(model)

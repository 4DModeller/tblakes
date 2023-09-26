# Load required libraries
library(INLA)
library(inlabru)
print("i never know what is going on")

# Load CSV file
data <- read.csv("repos/tblakes/data_for_4dm.csv")
# TODO : you need to normalize the data based on the year, not just the total
data$lake_change <- data$lake_growth + data$lake_decline
data$lake_change_norm <- scale(data$lake_change)
data$precip_norm <- scale(data$precip)
data$subarea_norm <- scale(data$SUB_AREA)
summary(data)
dim(data)
# Create mesh based on latitude and longitude coordinates
# mesh <- inla.mesh.2d(data$centroid_lon, data$centroid_lat, max.edge = 4, offset = 1)

# initial_range <- diff(range(data@data[, "LONG"])) / 5
initial_range <- diff(range(data$centroid_lon)) / 5

mesh <- inla.mesh.2d(data[c('centroid_lon', 'centroid_lat')]
                     # , max.edge = 4
                     , max.edge = c(1, 4)
                     # , offset = 1)
                     , offset = c(initial_range/4, initial_range)
                     , cutoff = 1)
#fdmr::mesh_builder(spatial_data = data)
plot(mesh)
prior_range <- initial_range

# A_hydGR = INLA::inla.spde.make.A(mesh_land,loc = grace_xyz, index = GRACE_indices_blocks,
#                                  block = base::seq(1,base::length(grace_xyz[,1]),by=1), block.rescale = "count",
#                                  group=GRACEobsdat$time, n.group=n_years)

# spde <- INLA::inla.spde2.pcmatern(
#   mesh = mesh,
#   prior.range = c(prior_range, 0.5),
#   prior.sigma = c(1, 0.01)
# )

spde_precip <- INLA::inla.spde.make.A()

rhoprior <- base::list(theta = list(prior = "pccor1", param = c(0, 0.9)))

group_index <- data$year
n_groups <- length(unique(data$year))

sp::coordinates(data) <- c("centroid_lon", "centroid_lat")

# formula <- lake_growth ~ 0 + ENDO + precip +
formula <- lake_change_norm ~ 0 + precip_norm + subarea_norm +
  f(
    main = coordinates,
    model = spde,
    group = group_index,
    ngroup = n_groups,
    control.group = list(
      model = "ar1",
      hyper = rhoprior
    )
  )

inlabru_model <- bru(formula, data = data,
                     family = "gaussian",
                     E = data$lake_growth,
                     control.family = list(link = "log"),
                     # control.predictor = list(link = 1),
                     options = list(
                       control.inla = list(
                         reordering = "metis",
                         int.strategy = "eb"),
                       verbose = TRUE,
                       # inla.mode="experimental"
                       inla.mode="classic"
                     )
)

# 
# # Create formula for regression model
# formula <- lake_growth ~ ENDO + precip + f(mesh, model = "ar1", group = "year")
# 
# # Create fixed effects matrix
# fixed_effects <- model.matrix(formula, data = data)
# 
# # Create spatial effect using mesh
# spatial_effect <- inla.spde2.pcmatern(mesh, alpha = c(2, 2))
# 
# # Combine fixed effects and spatial effect
# model_formula <- cbind(fixed_effects, spatial_effect)
# 
# # Fit the model using INLA
# model <- inla(formula = model_formula, data = data, family = "gaussian"
#               , control.predictor = list(compute = TRUE))

# Print the model summaryl
summary(inlabru_model)


use log::warn;
use std::collections::BTreeMap;

pub type ParameterList = BTreeMap<String, u64>;

//impl ParameterList {
//    pub fn new() -> Self {
//        ParameterList(BTreeMap::new())
//    }
//    pub fn insert(&mut self, name: String, value: u64) {
//        self.0.insert(name, value);
//    }
//    pub fn get_names(&self) -> Vec<String> {
//        self.0.keys().cloned().collect()
//    }
//    pub fn get(&self, name: &str) -> Option<&u64> {
//        self.0.get(name)
//    }
//    pub fn is_empty(&self) -> bool {
//        self.0.is_empty()
//    }
//    pub fn iter(&self) -> std::collections::btree_map::Iter<String, u64> {
//        self.0.iter()
//    }
//}

#[derive(Clone)]
pub struct Controller {
    pub name: String,
    pub size: Option<u64>,
    pub parameters: ParameterList,
    pub required_parameters: Vec<String>,
}

impl Controller {
    pub fn new(name: String, size: Option<u64>) -> Self {
        Controller {
            name,
            size,
            parameters: ParameterList::new(),
            required_parameters: Vec::new(),
        }
    }

    pub fn from_json(json_str: &str) -> Result<Self, std::io::Error> {
        let json_value: serde_json::Value = serde_json::from_str(json_str).unwrap();
        // Name
        if json_value.is_string() {
            let name = json_value.as_str().unwrap().to_string();
            return Ok(Controller::new(name, None));
        }
        let name: String;
        let name_option = json_value.get("controller_name"); //].as_str().unwrap().to_string();
        if name_option.is_none() {
            if json_value.get("name").is_some() {
                name = json_value["name"].as_str().unwrap().to_string();
            } else {
                panic!("Controller name not found");
            }
        } else {
            name = name_option.unwrap().as_str().unwrap().to_string();
        }
        // Size (optional)
        let size = json_value.get("size").map(|x| x.as_u64().unwrap());
        let mut controller = Controller::new(name, size);
        // Parameters (optional)
        let json_controller_params = json_value.get("custom_properties");
        if let Some(json_controller_params) = json_controller_params {
            for param in json_controller_params.as_array().unwrap() {
                let name = param
                    .get("name")
                    .expect("Parameter name not found")
                    .as_str()
                    .unwrap();
                let value = param
                    .get("value")
                    .expect("Parameter value not found")
                    .as_u64()
                    .unwrap();
                controller.add_parameter(name.to_string(), value);
            }
        }
        // Required parameters (optional)
        let required_parameters = json_value.get("required_parameters");
        if let Some(required_parameters) = required_parameters {
            for required_parameter in required_parameters.as_array().unwrap() {
                controller
                    .required_parameters
                    .push(required_parameter.as_str().unwrap().to_string());
            }
        }
        Ok(controller)
    }
    pub fn add_parameter(&mut self, name: String, value: u64) {
        self.parameters.insert(name, value);
    }
}

#[derive(Clone)]
pub struct Resource {
    pub name: String,
    pub slot: Option<u64>,
    pub size: Option<u64>,
    pub parameters: ParameterList,
    pub required_parameters: Vec<String>,
}

impl Resource {
    pub fn new(name: String, slot: Option<u64>, size: Option<u64>) -> Self {
        Resource {
            name,
            slot,
            size,
            parameters: ParameterList::new(),
            required_parameters: Vec::new(),
        }
    }
    pub fn from_json(json_str: &str) -> Result<Self, std::io::Error> {
        let json_value: serde_json::Value = serde_json::from_str(json_str).unwrap();
        // Name
        if json_value.is_string() {
            let name = json_value.as_str().unwrap().to_string();
            return Ok(Resource::new(name, None, None));
        }
        let name: String;
        let name_option = json_value.get("resource_name"); //].as_str().unwrap().to_string();
        if name_option.is_none() {
            if json_value.get("name").is_some() {
                name = json_value["name"].as_str().unwrap().to_string();
            } else {
                panic!("Resource name not found");
            }
        } else {
            name = name_option.unwrap().as_str().unwrap().to_string();
        }

        // Slot (optional)
        let slot = json_value.get("slot").map(|x| x.as_u64().unwrap());
        // Size (optional)
        let size = json_value.get("size").map(|x| x.as_u64().unwrap());
        let mut resource = Resource::new(name, slot, size);
        // Parameters (optional)
        let json_resource_params = json_value.get("custom_properties");
        if let Some(json_resource_params) = json_resource_params {
            let json_params_list = json_resource_params.as_array().unwrap();
            if json_params_list.is_empty() {
                for param in json_resource_params.as_array().unwrap() {
                    let name = param
                        .get("name")
                        .expect("Parameter name not found")
                        .as_str()
                        .unwrap();
                    let value = param
                        .get("value")
                        .expect("Parameter value not found")
                        .as_u64()
                        .unwrap();
                    resource.add_parameter(name.to_string(), value);
                }
            }
        }
        // Required parameters (optional)
        let required_parameters = json_value.get("required_parameters");
        if let Some(required_parameters) = required_parameters {
            for required_parameter in required_parameters.as_array().unwrap() {
                resource
                    .required_parameters
                    .push(required_parameter.as_str().unwrap().to_string());
            }
        }
        Ok(resource)
    }
    pub fn add_parameter(&mut self, name: String, value: u64) {
        self.parameters.insert(name, value);
    }
}

pub struct Cell {
    pub name: String,
    pub coordinates: Option<(u64, u64)>,
    pub controller: Option<Controller>,
    pub resources: Option<Vec<Resource>>,
    pub parameters: ParameterList,
    pub required_parameters: Vec<String>,
}

impl Cell {
    pub fn new(name: String, coordinates: Option<(u64, u64)>) -> Self {
        Cell {
            name,
            coordinates,
            controller: None,
            resources: None,
            parameters: ParameterList::new(),
            required_parameters: Vec::new(),
        }
    }

    pub fn from_json(json_str: &str) -> Result<Self, std::io::Error> {
        let json_value: serde_json::Value = serde_json::from_str(json_str).unwrap();
        // Name
        let name: String;
        let name_option = json_value.get("cell_name"); //].as_str().unwrap().to_string();
        if name_option.is_none() {
            if json_value.get("name").is_some() {
                name = json_value["name"].as_str().unwrap().to_string();
            } else {
                panic!("Cell name not found");
            }
        } else {
            name = name_option.unwrap().as_str().unwrap().to_string();
        }
        // Coordinates
        let coordinates_option = json_value.get("coordinates");
        let coordinates = if let Some(coordinates) = coordinates_option {
            Some((
                coordinates[0]["row"].as_u64().unwrap(),
                coordinates[0]["col"].as_u64().unwrap(),
            ))
        } else {
            warn!("Coordinates not found");
            None
        };

        let mut cell = Cell::new(name, coordinates);
        // Parameters
        let json_cell_params = json_value.get("custom_properties");
        if let Some(json_cell_params) = json_cell_params {
            for param in json_cell_params.as_array().unwrap() {
                let name = param
                    .get("name")
                    .expect("Parameter name not found")
                    .as_str()
                    .unwrap();
                let value = param
                    .get("value")
                    .expect("Parameter value not found")
                    .as_u64()
                    .unwrap();
                cell.add_parameter(name.to_string(), value);
            }
        }
        // Required parameters (optional)
        let required_parameters = json_value.get("required_parameters");
        if let Some(required_parameters) = required_parameters {
            for required_parameter in required_parameters.as_array().unwrap() {
                cell.required_parameters
                    .push(required_parameter.as_str().unwrap().to_string());
            }
        }
        // Controller (optional)
        let controller = json_value.get("controller");
        if let Some(controller) = controller {
            let controller_result = Controller::from_json(controller.to_string().as_str());
            if let Ok(controller) = controller_result {
                cell.controller = Some(controller);
            } else {
                warn!("Error parsing controller: {:?}", controller.to_string());
            }
        }
        // Resources (optional)
        let resources = json_value.get("resource_list");
        if let Some(resources) = resources {
            let mut resources_vec = Vec::new();
            for resource in resources.as_array().unwrap() {
                let resource_result = Resource::from_json(resource.to_string().as_str());
                if let Ok(resource_result) = resource_result {
                    resources_vec.push(resource_result);
                } else {
                    warn!("Error parsing resource: {:?}", resource.to_string());
                }
            }
            cell.resources = Some(resources_vec);
        }
        Ok(cell)
    }

    pub fn add_parameter(&mut self, name: String, value: u64) {
        self.parameters.insert(name, value);
    }
}

//impl std::fmt::Debug for Cell {
//    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
//        // Print following this format:
//        //{
//        //"coordinates": [
//        //  {
//        //    "row": 0,
//        //    "col": 0
//        //  }
//        //],
//        //"cell_name": "drra_cell_input"
//        //}
//        write!(f, "{{\n\"coordinates\": [\n{{\n\"row\": {},\n\"col\": {}\n}}\n],\n\"cell_name\": \"{}\"\n}}", self.coordinates.0, self.coordinates.1, self.name)
//    }
//}

#[derive(Debug)]
struct Npc {
    name: String,
    appearance: String,
    temperament: Option<String>,
    accent: Option<String>,
    phrases: Option<Vec<String>>,
    background: Option<String>,
    deceased: Option<bool>,
    // TODO look up actual stats
    stats_base: Option<String>,
}

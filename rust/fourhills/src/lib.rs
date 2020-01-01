#![recursion_limit = "128"]

use yew::services::ConsoleService;
use yew::{html, Component, ComponentLink, Html, ShouldRender};

pub struct Model {
    text: String,
    console: ConsoleService,
    // value: i64,
}

pub enum Msg {
    AddGoblin,
    // Increment,
    // Decrement,
    // Bulk(Vec<Msg>),
}

impl Component for Model {
    type Message = Msg;
    type Properties = ();

    fn create(_: Self::Properties, _: ComponentLink<Self>) -> Self {
        Model {
            text: "".to_owned(),
            console: ConsoleService::new(),
            // value: 0,
        }
    }

    fn update(&mut self, msg: Self::Message) -> ShouldRender {
        match msg {
            Msg::AddGoblin => {
                self.text.push_str("Goblin");
                self.console.log("Added goblin");
            }
            // Msg::Increment => {
            //     self.value = self.value + 1;
            //     self.console.log("plus one");
            // }
            // Msg::Decrement => {
            //     self.value = self.value - 1;
            //     self.console.log("minus one");
            // }
            // Msg::Bulk(list) => {
            //     for msg in list {
            //         self.update(msg);
            //         self.console.log("Bulk action");
            //     }
            // }
        }
        true
    }

    fn view(&self) -> Html<Self> {
        html! {
            <div>
                <nav class="menu">
                    <button onclick=|_| Msg::AddGoblin>{ "Add Goblin" }</button>
                    // <button onclick=|_| Msg::Increment>{ "Increment" }</button>
                    // <button onclick=|_| Msg::Decrement>{ "Decrement" }</button>
                    // <button onclick=|_| Msg::Bulk(vec![Msg::Increment, Msg::Increment])>{ "Increment Twice" }</button>
                </nav>
                <p>{ &self.text }</p>
                // <p>{ Date::new().to_string() }</p>
            </div>
        }
    }
}
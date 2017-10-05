function programmer_init(){
     $("#buttonGroup").jqxButtonGroup({ mode: 'default' });

    var fields = [
              { name: "status", map: "state", type: "string" },
              { name: "text", map: "label", type: "string" },
              { name: "tags", type: "string" },
              { name: "color", map: "hex", type: "string" },
              { name: "resourceId", type: "number" }
    ];
    var source =
     {
         localData: [
                  { state: "new", label: "Combine Orders", tags: "orders, combine", hex: "#5dc3f0", resourceId: 3 },
                  { state: "new", label: "Change Billing Address", tags: "billing", hex: "#f19b60", resourceId: 1 },
                  { state: "new", label: "One item added to the cart", tags: "cart", hex: "#5dc3f0", resourceId: 3 },
                  { state: "new", label: "Edit Item Price", tags: "price, edit", hex: "#5dc3f0", resourceId: 4 },
                  { state: "new", label: "Login 404 issue", tags: "issue, login", hex: "#6bbd49" }
         ],
         dataType: "array",
         dataFields: fields
     };
    var dataAdapter = new $.jqx.dataAdapter(source);
    var resourcesAdapterFunc = function () {
        var resourcesSource =
        {
            localData: [
                  { id: 0, name: "No name", image: "static/images/arrow-go-left-300px.png", common: true },
                  { id: 1, name: "Andrew Fuller", image: "static/images/arrow-go-left-300px.png" },
                  { id: 2, name: "Janet Leverling", image: "static/images/arrow-go-right-300px.png" },
                  { id: 3, name: "Steven Buchanan", image: "static/images/arrow-go-left-300px.png" },
                  { id: 4, name: "Nancy Davolio", image: "static/images/arrow-go-left-300px.png" },
                  { id: 5, name: "Michael Buchanan", image: "../../images/Michael.png" },
                  { id: 6, name: "Margaret Buchanan", image: "../../images/margaret.png" },
                  { id: 7, name: "Robert Buchanan", image: "../../images/robert.png" },
                  { id: 8, name: "Laura Buchanan", image: "../../images/Laura.png" },
                  { id: 9, name: "Laura Buchanan", image: "../../images/Anne.png" }
            ],
            dataType: "array",
            dataFields: [
                 { name: "id", type: "number" },
                 { name: "name", type: "string" },
                 { name: "image", type: "string" },
                 { name: "common", type: "boolean" }
            ]
        };
        var resourcesDataAdapter = new $.jqx.dataAdapter(resourcesSource);
        return resourcesDataAdapter;
    }


     $('#kanban1').jqxKanban({
        width: '100%',
        height: '100%',
        resources: resourcesAdapterFunc(),
        source: dataAdapter,
        connectWith: "#kanban2, #kanban3",
        columns: [
            { text: "Backlog", dataField: "new", maxItems: 10 }
        ],
        columnRenderer: function (element, collapsedElement, column) {
            var columnItems = $("#kanban1").jqxKanban('getColumnItems', column.dataField).length;
            element.find(".jqx-kanban-column-header-status").html(" (" + columnItems + "/" + column.maxItems + ")");
            collapsedElement.find(".jqx-kanban-column-header-status").html(" (" + columnItems + "/" + column.maxItems + ")");
        }
    });
}
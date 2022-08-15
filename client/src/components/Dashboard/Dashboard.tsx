import React, { useRef, useState } from "react";
import {
  Stack,
  Toggle,
  DetailsList,
  SelectionMode,
  IColumn,
  Text,
  TextField,
  DefaultButton,
  PrimaryButton,
  Pivot,
  PivotItem,
  Label,
} from "@fluentui/react";

import Cytoscape from "cytoscape";
import Dagre from "cytoscape-dagre";
import CytoscapeComponent from "react-cytoscapejs";

Cytoscape.use(Dagre);

const Dashboard: React.FunctionComponent = () => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [isEdgeShows, setIsEdgeShows] = useState<boolean | undefined>(true);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [isPartShows, setIsPartShows] = useState<boolean | undefined>(true);
  const cyRef = useRef<Cytoscape.Core>();

  const timeColumns: IColumn[] = [
    {
      key: "tag",
      name: "Time",
      onRender: (item) => <Text>{item.tag}</Text>,
    } as IColumn,
    {
      key: "value",
      name: "",
      onRender: (item) => <Text>{item.value}</Text>,
    } as IColumn,
  ];

  const arrivalColumns: IColumn[] = [
    {
      key: "tag",
      name: "Arrival",
      onRender: (item) => <Text>{item.tag}</Text>,
    } as IColumn,
    {
      key: "value",
      name: "",
      onRender: (item) => <Text>{item.value}</Text>,
    } as IColumn,
  ];

  const amountColumns: IColumn[] = [
    {
      key: "tag",
      name: "Amount",
      onRender: (item) => <Text>{item.tag}</Text>,
    } as IColumn,
    {
      key: "value",
      name: "",
      onRender: (item) => <Text>{item.value}</Text>,
    } as IColumn,
  ];

  const elements = [
    { data: { id: "S1", label: "S1" } },
    { data: { id: "S2", label: "S2" } },
    { data: { id: "S3", label: "S3" } },
    { data: { id: "M1_1", label: "M1_1" } },
    { data: { id: "M1_2", label: "M1_2" } },
    { data: { id: "M2", label: "M2" } },
    { data: { id: "M3", label: "M3" } },
    { data: { id: "M4", label: "M4" } },
    { data: { id: "M5", label: "M5" } },
    { data: { id: "E1", label: "E1" } },
    { data: { source: "S1", target: "M1_1", label: "S1 -> M1_1" } },
    { data: { source: "S2", target: "M1_2", label: "S2 -> M1_2" } },
    { data: { source: "S3", target: "M5", label: "S3 -> M5" } },
    { data: { source: "M1_1", target: "M2", label: "M1_1 -> M2" } },
    { data: { source: "M1_2", target: "M2", label: "M1_2 -> M2" } },
    { data: { source: "M2", target: "M3", label: "M2 -> M3" } },
    { data: { source: "M3", target: "M4", label: "M3 -> M4" } },
    { data: { source: "M4", target: "M5", label: "M4 -> M5" } },
    { data: { source: "M5", target: "E1", label: "M5 -> E1" } },
  ];

  const layout = { name: "dagre", rankDir: "LR" };

  return (
    <Stack
      horizontal
      horizontalAlign="center"
      verticalAlign="center"
      verticalFill
    >
      <Stack
        verticalFill
        tokens={{ childrenGap: 10 }}
        style={{ flex: 1, padding: 10 }}
      >
        <div style={{ paddingLeft: 10, paddingTop: 10 }}>
          <Toggle
            label="Show Edges"
            inlineLabel
            onChange={(ev, checked?: boolean) => setIsEdgeShows(checked)}
          />
          <Toggle
            label="Show Parts"
            inlineLabel
            onChange={(ev, checked?: boolean) => setIsPartShows(checked)}
          />
        </div>
        <DetailsList
          selectionMode={SelectionMode.none}
          columns={timeColumns}
          items={[
            { tag: "Current Time", value: "[hh:mm]" },
            { tag: "Shift End Time", value: "[hh:mm]" },
            { tag: "Remaining Time", value: "[hh:mm]" },
          ]}
        />
        <DetailsList
          selectionMode={SelectionMode.none}
          columns={arrivalColumns}
          items={[
            { tag: "Avg. Arrival", value: "[hh:mm]" },
            { tag: "Last Product", value: "[hh:mm]" },
          ]}
        />
        <DetailsList
          selectionMode={SelectionMode.none}
          columns={amountColumns}
          items={[
            { tag: "Current Amount", value: "XXX" },
            { tag: "Planned Amount", value: "XXX" },
            { tag: "Amount left", value: "XXX" },
            { tag: "Estimated Amount", value: "XXX" },
          ]}
        />
      </Stack>

      <Stack verticalFill style={{ flex: 4 }}>
        <CytoscapeComponent
          elements={elements}
          layout={layout}
          cy={(cy) => {
            cyRef.current = cy;
            cy.layout(layout).run();
          }}
          style={{ width: "100%", height: "100%" }}
        />
      </Stack>

      <Stack
        verticalFill
        tokens={{ childrenGap: 5 }}
        style={{ flex: 1, padding: 10 }}
      >
        <TextField label="Simulation duration" />
        <Stack horizontal horizontalAlign="end" tokens={{ childrenGap: 20 }}>
          <DefaultButton text="Reset" onClick={() => alert("Reset")} />
          <PrimaryButton text="Simulate" onClick={() => alert("Simulate")} />
        </Stack>
        <Stack>
          <Pivot>
            <PivotItem headerText="Info">
              <Label>More information</Label>
            </PivotItem>
            <PivotItem headerText="History">
              <Label>Parts history</Label>
            </PivotItem>
            <PivotItem headerText="Sensor">
              <Label>Sensors time-series</Label>
            </PivotItem>
          </Pivot>
        </Stack>
      </Stack>
    </Stack>
  );
};

export default Dashboard;

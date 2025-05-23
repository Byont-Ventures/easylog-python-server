/* tslint:disable */
/* eslint-disable */
/**
 * FastAPI No description provided (generated by Openapi Generator
 * https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 0.1.0
 *
 * NOTE: This class is auto generated by OpenAPI Generator
 * (https://openapi-generator.tech). https://openapi-generator.tech Do not edit
 * the class manually.
 */

import { mapValues } from '../runtime';
/**
 * @export
 * @interface AgentConfig
 */
export interface AgentConfig {
  [key: string]: any | any;
  /**
   * @memberof AgentConfig
   * @type {string}
   */
  agent_class: string;
}

/** Check if a given object implements the AgentConfig interface. */
export function instanceOfAgentConfig(value: object): value is AgentConfig {
  if (!('agent_class' in value) || value['agent_class'] === undefined)
    return false;
  return true;
}

export function AgentConfigFromJSON(json: any): AgentConfig {
  return AgentConfigFromJSONTyped(json, false);
}

export function AgentConfigFromJSONTyped(
  json: any,
  ignoreDiscriminator: boolean
): AgentConfig {
  if (json == null) {
    return json;
  }
  return {
    ...json,
    agent_class: json['agent_class']
  };
}

export function AgentConfigToJSON(json: any): AgentConfig {
  return AgentConfigToJSONTyped(json, false);
}

export function AgentConfigToJSONTyped(
  value?: AgentConfig | null,
  ignoreDiscriminator: boolean = false
): any {
  if (value == null) {
    return value;
  }

  return {
    ...value,
    agent_class: value['agent_class']
  };
}

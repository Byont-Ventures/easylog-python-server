/* tslint:disable */
/* eslint-disable */
/**
 * Easylog No description provided (generated by Openapi Generator
 * https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 0.2.0
 *
 * NOTE: This class is auto generated by OpenAPI Generator
 * (https://openapi-generator.tech). https://openapi-generator.tech Do not edit
 * the class manually.
 */

import { mapValues } from '../runtime';
/**
 * @export
 * @interface ResourceResource
 */
export interface ResourceResource {
  /**
   * @memberof ResourceResource
   * @type {number}
   */
  id?: number;
  /**
   * Use this field to display to the user
   *
   * @memberof ResourceResource
   * @type {string}
   */
  label?: string;
  /**
   * @memberof ResourceResource
   * @type {string}
   */
  name?: string;
  /**
   * This is the name field slugified
   *
   * @memberof ResourceResource
   * @type {string}
   */
  slug?: string;
}

/** Check if a given object implements the ResourceResource interface. */
export function instanceOfResourceResource(
  value: object
): value is ResourceResource {
  return true;
}

export function ResourceResourceFromJSON(json: any): ResourceResource {
  return ResourceResourceFromJSONTyped(json, false);
}

export function ResourceResourceFromJSONTyped(
  json: any,
  ignoreDiscriminator: boolean
): ResourceResource {
  if (json == null) {
    return json;
  }
  return {
    id: json['id'] == null ? undefined : json['id'],
    label: json['label'] == null ? undefined : json['label'],
    name: json['name'] == null ? undefined : json['name'],
    slug: json['slug'] == null ? undefined : json['slug']
  };
}

export function ResourceResourceToJSON(json: any): ResourceResource {
  return ResourceResourceToJSONTyped(json, false);
}

export function ResourceResourceToJSONTyped(
  value?: ResourceResource | null,
  ignoreDiscriminator: boolean = false
): any {
  if (value == null) {
    return value;
  }

  return {
    id: value['id'],
    label: value['label'],
    name: value['name'],
    slug: value['slug']
  };
}

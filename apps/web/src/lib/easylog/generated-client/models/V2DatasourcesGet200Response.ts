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
import type { Datasource } from './Datasource';
import {
  DatasourceFromJSON,
  DatasourceFromJSONTyped,
  DatasourceToJSON,
  DatasourceToJSONTyped
} from './Datasource';
import type { PaginationLinks } from './PaginationLinks';
import {
  PaginationLinksFromJSON,
  PaginationLinksFromJSONTyped,
  PaginationLinksToJSON,
  PaginationLinksToJSONTyped
} from './PaginationLinks';
import type { PaginationMeta } from './PaginationMeta';
import {
  PaginationMetaFromJSON,
  PaginationMetaFromJSONTyped,
  PaginationMetaToJSON,
  PaginationMetaToJSONTyped
} from './PaginationMeta';

/**
 * @export
 * @interface V2DatasourcesGet200Response
 */
export interface V2DatasourcesGet200Response {
  /**
   * @memberof V2DatasourcesGet200Response
   * @type {PaginationLinks}
   */
  links?: PaginationLinks;
  /**
   * @memberof V2DatasourcesGet200Response
   * @type {PaginationMeta}
   */
  meta?: PaginationMeta;
  /**
   * @memberof V2DatasourcesGet200Response
   * @type {Datasource[]}
   */
  data?: Array<Datasource>;
}

/** Check if a given object implements the V2DatasourcesGet200Response interface. */
export function instanceOfV2DatasourcesGet200Response(
  value: object
): value is V2DatasourcesGet200Response {
  return true;
}

export function V2DatasourcesGet200ResponseFromJSON(
  json: any
): V2DatasourcesGet200Response {
  return V2DatasourcesGet200ResponseFromJSONTyped(json, false);
}

export function V2DatasourcesGet200ResponseFromJSONTyped(
  json: any,
  ignoreDiscriminator: boolean
): V2DatasourcesGet200Response {
  if (json == null) {
    return json;
  }
  return {
    links:
      json['links'] == null
        ? undefined
        : PaginationLinksFromJSON(json['links']),
    meta:
      json['meta'] == null ? undefined : PaginationMetaFromJSON(json['meta']),
    data:
      json['data'] == null
        ? undefined
        : (json['data'] as Array<any>).map(DatasourceFromJSON)
  };
}

export function V2DatasourcesGet200ResponseToJSON(
  json: any
): V2DatasourcesGet200Response {
  return V2DatasourcesGet200ResponseToJSONTyped(json, false);
}

export function V2DatasourcesGet200ResponseToJSONTyped(
  value?: V2DatasourcesGet200Response | null,
  ignoreDiscriminator: boolean = false
): any {
  if (value == null) {
    return value;
  }

  return {
    links: PaginationLinksToJSON(value['links']),
    meta: PaginationMetaToJSON(value['meta']),
    data:
      value['data'] == null
        ? undefined
        : (value['data'] as Array<any>).map(DatasourceToJSON)
  };
}

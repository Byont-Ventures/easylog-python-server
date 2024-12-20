/* tslint:disable */
/* eslint-disable */
/**
 * FastAPI
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 0.1.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */

import { mapValues } from '../runtime';
import type { AgentConfig } from './AgentConfig';
import {
    AgentConfigFromJSON,
    AgentConfigFromJSONTyped,
    AgentConfigToJSON,
    AgentConfigToJSONTyped,
} from './AgentConfig';
import type { MessageContent } from './MessageContent';
import {
    MessageContentFromJSON,
    MessageContentFromJSONTyped,
    MessageContentToJSON,
    MessageContentToJSONTyped,
} from './MessageContent';

/**
 * 
 * @export
 * @interface MessageCreateInput
 */
export interface MessageCreateInput {
    /**
     * The content of the message.
     * @type {Array<MessageContent>}
     * @memberof MessageCreateInput
     */
    content: Array<MessageContent>;
    /**
     * The configuration for the agent that generated the message. Requires at least a `agent_class` key.
     * @type {AgentConfig}
     * @memberof MessageCreateInput
     */
    agent_config: AgentConfig;
}

/**
 * Check if a given object implements the MessageCreateInput interface.
 */
export function instanceOfMessageCreateInput(value: object): value is MessageCreateInput {
    if (!('content' in value) || value['content'] === undefined) return false;
    if (!('agent_config' in value) || value['agent_config'] === undefined) return false;
    return true;
}

export function MessageCreateInputFromJSON(json: any): MessageCreateInput {
    return MessageCreateInputFromJSONTyped(json, false);
}

export function MessageCreateInputFromJSONTyped(json: any, ignoreDiscriminator: boolean): MessageCreateInput {
    if (json == null) {
        return json;
    }
    return {
        
        'content': ((json['content'] as Array<any>).map(MessageContentFromJSON)),
        'agent_config': AgentConfigFromJSON(json['agent_config']),
    };
}

export function MessageCreateInputToJSON(json: any): MessageCreateInput {
    return MessageCreateInputToJSONTyped(json, false);
}

export function MessageCreateInputToJSONTyped(value?: MessageCreateInput | null, ignoreDiscriminator: boolean = false): any {
    if (value == null) {
        return value;
    }

    return {
        
        'content': ((value['content'] as Array<any>).map(MessageContentToJSON)),
        'agent_config': AgentConfigToJSON(value['agent_config']),
    };
}


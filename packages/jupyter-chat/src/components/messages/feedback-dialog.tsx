import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  CircularProgress,
  Alert,
  Typography
} from '@mui/material';
import React, { useState } from 'react';
import { IChatModel } from '../../model';

export interface IFeedbackDialogProps {
  open: boolean;
  onClose: () => void;
  messageBody?: string;
  model?: IChatModel;
  messageIndex?: number;
}

export function FeedbackDialog(props: IFeedbackDialogProps): JSX.Element {
  const { open, onClose, messageBody, model, messageIndex } = props;
  const [feedback, setFeedback] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleClose = () => {
    setFeedback('');
    setError(null);
    setSuccess(false);
    onClose();
  };

  const getPreviousUserMessage = (): string => {
    if (!model || messageIndex === undefined) {
      return '';
    }

    // Look backwards from the current message to find the previous user message
    for (let i = messageIndex - 1; i >= 0; i--) {
      const msg = model.messages[i];
      if (msg && !msg.sender.bot && !msg.deleted) {
        return msg.body || '';
      }
    }
    return '';
  };

  const getConversationId = (): string => {
    const modelWithId = model as any;
    return String(modelWithId._id);
  };

  const handleSubmit = async () => {
    if (!feedback.trim()) {
      setError('Please enter feedback before submitting');
      return;
    }

    const feedbackUrl = process.env.TWD_FEEDBACK_LOGGING_FLOW;
    if (!feedbackUrl) {
      setError('Feedback URL not configured.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const conversationId = getConversationId();
      const question = getPreviousUserMessage();
      const answer = messageBody || '';

      const response = await fetch(feedbackUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          question: question,
          answer: answer,
          feedback: feedback
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      setSuccess(true);
      setTimeout(() => {
        handleClose();
      }, 1500);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to submit feedback'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Give Feedback</DialogTitle>
      <DialogContent>
        <Box sx={{ paddingTop: 0.5 }}>
          <Alert severity="info" sx={{ marginBottom: 2 }}>
            <Typography variant="body2">
              By submitting feedback, your chat conversation and this message
              will be read by SWEG for quality improvement purposes. Your
              feedback is anonymous.
            </Typography>
          </Alert>
          {error && (
            <Alert severity="error" sx={{ marginBottom: 2 }}>
              {error}
            </Alert>
          )}
          {success && (
            <Alert severity="success" sx={{ marginBottom: 2 }}>
              Feedback submitted successfully!
            </Alert>
          )}
          <TextField
            autoFocus
            multiline
            rows={4}
            fullWidth
            label="Your Feedback"
            placeholder="Please describe the feedback with this message..."
            value={feedback}
            onChange={e => setFeedback(e.target.value)}
            disabled={loading || success}
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading || success}
          startIcon={loading && <CircularProgress size={16} />}
        >
          {loading ? 'Submitting...' : 'Submit'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
